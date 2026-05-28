// https://developer.mozilla.org/en/JavaScript/Reference/Global_Objects/Function/bind
if (!Function.prototype.bind) {
	Function.prototype.bind = function (oThis) {
		if (typeof this !== "function") {
			// closest thing possible to the ECMAScript 5 internal IsCallable function
			throw new TypeError("Function.prototype.bind - what is trying to be bound is not callable");
		}

		var aArgs = Array.prototype.slice.call(arguments, 1), 
        	fToBind = this, 
        	fNOP = function () {},
        	fBound = function () {
        		return fToBind.apply(this instanceof fNOP && oThis
                                 ? this
                                 : oThis,
                               aArgs.concat(Array.prototype.slice.call(arguments)));
        };

        fNOP.prototype = this.prototype;
        fBound.prototype = new fNOP();

        return fBound;
	};
}

var module_name = 'campaign_monitoring';
var App = null;
var idCampaign = '';
var paramsType = '';
var count = '';


//Redireccionar la página entera en caso de que la sesión se haya perdido
function verificar_error_session(respuesta)
{
	if (respuesta['statusResponse'] == 'ERROR_SESSION') {
		if (respuesta['error'] != null && respuesta['error'] != '')
			alert(respuesta['error']);
		window.open('index.php', '_self');
	}
}

$(document).ready(function() {
	$('#issabel-callcenter-error-message').hide();
	
	// Inicialización de Ember.js
	App = Ember.Application.create({
/*
		LOG_TRANSITIONS: true,
		LOG_ACTIVE_GENERATION: true,
		LOG_VIEW_LOOKUPS: true,
*/
		rootElement:	'#campaignMonitoringApplication'
	});
	
	App.Router.map(function() {
		this.resource('campaign', { path: '/' }, function () {
			this.route('details', { path: '/details/:type/:id_campaign' });
		});
	});

	App.CampaignSelect = Ember.Select.extend({
		optionView: Ember.SelectOption.extend({
			classNameBindings: ['statusClass'],
			statusClass: function() {
				var content = this.get('content');
				if (content) {
					var status = content.get('status');
					if (status === 'A' || status === 'active' || status === 'activequeue') {
						return 'campaign-status-active';
					} else if (status === 'I' || status === 'inactive') {
						return 'campaign-status-inactive';
					} else if (status === 'T' || status === 'finished' || status === 'terminada') {
						return 'campaign-status-finished';
					}
				}
				return '';
			}.property('content.status')
		})
	});

	App.CampaignRoute = Ember.Route.extend({
		model: function(params) {
			return $.get('index.php', {
				menu:		module_name, 
				rawmode:	'yes',
				action:		'getCampaigns'
			}, 'json').then(function(respuesta) {
				verificar_error_session(respuesta);
				if (respuesta.status == 'error') {
					mostrar_mensaje_error(respuesta.message);
					return;
				}
				return respuesta.campaigns.map(function(item) {
					return App.CampaignSummary.create(item);
				});
			});
		}
	});
	
	App.CampaignDetailsRoute = Ember.Route.extend({
		model: function(params) {
			return $.get('index.php', {
				menu:			module_name, 
				rawmode:		'yes',
				action:			'getCampaignDetail',
				campaigntype:	params.type,
				campaignid:		params.id_campaign
			}, 'json').then(function(respuesta) {
				verificar_error_session(respuesta);
				if (respuesta.status == 'error') {
					mostrar_mensaje_error(respuesta.message);
					return null;
				}
				paramsType = params.type;
				idCampaign = params.id_campaign;
				count = 0;
				return App.CampaignDetails.create({
					type:				params.type,
					id_campaign:		params.id_campaign,
					outgoing:			(params.type == 'outgoing'),
					fechaInicio:		respuesta.campaigndata.startdate,
					fechaFinal:			respuesta.campaigndata.enddate,
					horaInicio:			respuesta.campaigndata.working_time_starttime,
					horaFinal:			respuesta.campaigndata.working_time_endtime,
					cola:				respuesta.campaigndata.queue,
					maxIntentos:		respuesta.campaigndata.retries,
					
					respuesta:			respuesta
				});
			});
		},
		setupController: function (controller, model) {
			var parentController = this.controllerFor("campaign");
			var old_key_campaign = parentController.get('key_campaign');
			var new_key_campaign = model.get('type') + '-' + model.get('id_campaign');
			if (old_key_campaign == null || old_key_campaign != new_key_campaign) {
				parentController.set('key_campaign', new_key_campaign);
			}
			
			controller.clear();
			controller.set('model', model);
			controller.manejarRespuestaStatus(model.get('respuesta'));
			model.set('respuesta', null);

			// Lanzar el callback que actualiza el estado de la llamada
		    setTimeout(controller.do_checkstatus.bind(controller), 1);
		},
		serialize: function(model, parameters) {
			return { type: model.get('type'), id_campaign: model.get('id_campaign') };
		}		
	});

	/* El siguiente controlador es el controlador de más alto nivel. Este 
	 * controlador contiene la lista de campañas disponibles, y muestra la vista
	 * de la campaña elegida. */
	App.CampaignController = Ember.ArrayController.extend({
		key_campaign: null,
		loadDetails: function () {
			var campaign = this.findBy('key_campaign', this.get('key_campaign'));
			if (campaign == null) {
				console.error('Failed to find key_campaign='+this.get('key_campaign'));
				return;
			}
			var targetPath = '/details/' + campaign.get('type') + '/' + campaign.get('id_campaign');
			this.get('target').transitionTo(targetPath);
		}.observes('key_campaign')
	});

	/* El siguiente objeto describe una campaña cargada en la lista de campañas. */
	App.CampaignSummary = Ember.Object.extend({
		id_campaign:	null,
		desc_campaign:	null,
		type:			null,
		status:			null,
		key_campaign:	function() {
			return this.get('type') + '-' + this.get('id_campaign');
		}.property('type', 'id_campaign'),
		label_with_status: function() {
			var desc = this.get('desc_campaign');
			var status = this.get('status');
			var prefix = '';
			if (status === 'A' || status === 'active' || status === 'activequeue') {
				prefix = '🟢 ';
			} else if (status === 'I' || status === 'inactive') {
				prefix = '🟡 ';
			} else if (status === 'T' || status === 'finished' || status === 'terminada') {
				prefix = '🔴 ';
			} else {
				prefix = '⚪ ';
			}
			return prefix + desc;
		}.property('desc_campaign', 'status')
	});

	App.CampaignDetails = Ember.Object.extend({
		type:				null,
		id_campaign:		null,
		outgoing:			false,
		fechaInicio:		'...',
		fechaFinal:			'...',
		horaInicio:			'...',
		horaFinal:			'...',
		cola:				'...',
		maxIntentos:		'...',
		
		respuesta:			null
	});
	
	App.estadosFiltro = ['Todos', 'Libre', 'Ocupado', 'En descanso', 'No logon'];

	App.CampaignDetailsController = Ember.ObjectController.extend({
		estadoClienteHash:	null,		
		longPoll:			null,	// Objeto de POST largo
		evtSource:			null,	// Objeto EventSource, si está soportado por el navegador
		timerReciente:		null,

		llamadas:       	null,
		llamadasMarcando:	null,
		agentes:			null,
		registroVisible: false,
		registro:			null,
		filtroEstado: 'Todos',
		filtroExtension: '',

		resumenAgentes: function() {
			var agentes = this.get('agentes') || [];
			var extPrefix = this.get('filtroExtension');

			// Filtrar agentes por el prefijo de la extensión
			if (extPrefix && extPrefix.trim() !== '') {
				var prefix = extPrefix.trim();
				agentes = agentes.filter(function(agent) {
					var canal = agent.get('canal') || '';
					var matches = canal.match(/(?:PJSIP|SIP|IAX2|Local)\/(\d+)/i);
					var ext = matches ? matches[1] : '';
					return ext.indexOf(prefix) === 0;
				});
			}

			var total = agentes.length;
			var libre = 0;
			var ocupado = 0;
			var descanso = 0;
			var nologon = 0;

			agentes.forEach(function(agent) {
				var statusLower = (agent.get('estado') || '').toLowerCase();
				var isLoggedOut = statusLower.indexOf('no logon') !== -1 || 
				                  statusLower.indexOf('logged out') !== -1 || 
				                  statusLower.indexOf('no logoneado') !== -1 ||
				                  statusLower.indexOf('déconnecté') !== -1;
				var isFree = statusLower.indexOf('libre') !== -1 || 
				             statusLower.indexOf('free') !== -1 || 
				             statusLower.indexOf('boşta') !== -1;
				var isBusy = statusLower.indexOf('ocupado') !== -1 || 
				             statusLower.indexOf('busy') !== -1 || 
				             statusLower.indexOf('oncall') !== -1 ||
				             statusLower.indexOf('on call') !== -1;
				var isBreak = statusLower.indexOf('break') !== -1 || 
				              statusLower.indexOf('descanso') !== -1 || 
				              statusLower.indexOf('pause') !== -1 || 
				              statusLower.indexOf('paused') !== -1;

				if (isLoggedOut) nologon++;
				else if (isBusy) ocupado++;
				else if (isBreak) descanso++;
				else if (isFree) libre++;
			});

			return {
				total: total,
				libre: libre,
				ocupado: ocupado,
				descanso: descanso,
				nologon: nologon
			};
		}.property('agentes.@each.estado', 'filtroExtension'),

		agentesFiltrados: function() {
			var estado = this.get('filtroEstado');
			var extPrefix = this.get('filtroExtension');
			var agentes = this.get('agentes');
			if (!agentes) return [];

			return agentes.filter(function(agent) {
				// 1. Filtrar por estado
				if (estado !== 'Todos') {
					var agentStatus = agent.get('estado') || '';
					var statusLower = agentStatus.toLowerCase();
					
					if (estado === 'No logon') {
						var isLoggedOut = statusLower.indexOf('no logon') !== -1 || 
						                  statusLower.indexOf('logged out') !== -1 || 
						                  statusLower.indexOf('no logoneado') !== -1 ||
						                  statusLower.indexOf('déconnecté') !== -1;
						if (!isLoggedOut) return false;
					} else if (estado === 'Libre') {
						var isFree = statusLower.indexOf('libre') !== -1 || 
						             statusLower.indexOf('free') !== -1 || 
						             statusLower.indexOf('boşta') !== -1;
						if (!isFree) return false;
					} else if (estado === 'Ocupado') {
						var isBusy = statusLower.indexOf('ocupado') !== -1 || 
						             statusLower.indexOf('busy') !== -1 || 
						             statusLower.indexOf('oncall') !== -1 ||
						             statusLower.indexOf('on call') !== -1;
						if (!isBusy) return false;
					} else if (estado === 'En descanso') {
						var isBreak = statusLower.indexOf('break') !== -1 || 
						              statusLower.indexOf('descanso') !== -1 || 
						              statusLower.indexOf('pause') !== -1 || 
						              statusLower.indexOf('paused') !== -1;
						if (!isBreak) return false;
					}
				}

				// 2. Filtrar por prefijo de extension
				if (extPrefix && extPrefix.trim() !== '') {
					var prefix = extPrefix.trim();
					var canal = agent.get('canal') || '';
					var matches = canal.match(/(?:PJSIP|SIP|IAX2|Local)\/(\d+)/i);
					var ext = matches ? matches[1] : '';
					if (ext.indexOf(prefix) !== 0) {
						return false;
					}
				}

				return true;
			});
		}.property('agentes.@each.estado', 'agentes.@each.canal', 'filtroEstado', 'filtroExtension'),
		alturaLlamada: function() {
			return this.get('registroVisible') ? 'height: 180px;' : 'height: 400px;';
		}.property('registroVisible'),
		
		init: function() {
			this.clear();

			// Iniciar timer regular para marcar los elementos recientes
			this.timerReciente = setInterval(function() {
				var fechaDiff = new Date();
				var callback = function (item) {
					if (item.get('reciente')) {
						var fechaInicio = item.get('rtime');
						if (fechaDiff.getTime() - fechaInicio.getTime() > 2000) {
							item.set('reciente', false);
						}
					}
				};
				this.llamadasMarcando.forEach(callback);
				this.agentes.forEach(callback);
			}.bind(this), 500);
			
			// Instalar manejador de finalización de la página para limpiar SSE
			$(window).unload(function() {
				this.clear();
				clearInterval(this.timerReciente);
			}.bind(this));
		},
		clear: function () {
			// Cancelar Server Sent Events de campaña anterior
			if (this.evtSource != null) {
				this.evtSource.onmessage = function(event) {
					console.warn("This evtSource was closed but still receives messages!");
				}
				this.evtSource.close();
				this.evtSource = null;
			}
			if (this.longPoll != null) {
				this.longPoll.abort();
				this.longPoll = null;
			}

			this.set('llamadas', App.StatLlamadas.create());
			this.set('llamadasMarcando', [
          			/*
    				Ember.Object.create({
    					callid: 875,
    					numero: '11111',
    					troncal: 'SIP/gato',
    					estado: 'Dialing',
    					desde: '00:01:02',
    					rtime: new Date(),
    					reciente: true})
    			*/
    		]);
			this.set('agentes', [
         			/*
    				Ember.Object.create({
    					canal: 'Agent/9000',
    					estado: 'No logon',
    					numero: '???',
    					troncal: 'SIP/gato',
    					desde: '00:01:02',
    					rtime: new Date(),
    					reciente: true})
    			*/
    		]);
			this.set('registro', [
      		    // No es necesario Ember.Object porque no se espera modificar los valores
    			//{timestamp: '10:59:00', mensaje: 'Esta es una prueba'}
    		]);
		},
		do_checkstatus: function() {
			var params = {
					menu:		module_name, 
					rawmode:	'yes',
					action:		'checkStatus',
					clientstatehash: this.get('estadoClienteHash')
				};

			//if (window.EventSource) {
				/*params['serverevents'] = true;
				this.evtSource = new EventSource('index.php?' + $.param(params));
				this.evtSource.onmessage = function(event) {
					this.manejarRespuestaStatus($.parseJSON(event.data));
				}.bind(this);
				this.evtSource.onerror = function(event) {
					event.target.close();
				}.bind(this);
			} else {*/
				this.longPoll = $.get('index.php', params, function (respuesta) {
					verificar_error_session(respuesta);
					if (this.manejarRespuestaStatus(respuesta)) {
						// Lanzar el método de inmediato
						setTimeout(this.do_checkstatus.bind(this), 1);
					}
				}.bind(this), 'json');
			//}
		},
		manejarRespuestaStatus: function(respuesta) {
			// Intentar recargar la página en caso de error
			if (respuesta.error != null) {
				window.alert(respuesta.error);
				location.reload();
				return false;
			}

			// Verificar el hash del estado del cliente
			if (respuesta.estadoClienteHash == 'invalidated') {
				// Espera ha sido invalidada por cambio de campaña a monitorear
				return false;
			}
			if (respuesta.estadoClienteHash == 'mismatch') {
				/* Ha ocurrido un error y se ha perdido sincronía. Si el hash que 
				 * recibió es distinto a this.get('estadoClienteHash') 
				 * entonces esta es una petición vieja. Si es idéntico debe de recargase
				 * la página.
				 */
				if (respuesta.hashRecibido == this.get('estadoClienteHash')) {
					// Realmente se ha perdido sincronía
					console.error("Lost synchronization with server, reloading page...");
					location.reload();
				} else {
					// Se ha recibido respuesta luego de que supuestamente se ha parado
					console.warn("Received mismatch from stale SSE session, ignoring...");
				}
				return false;
			}
			this.set('estadoClienteHash', respuesta.estadoClienteHash);
			
			// Estado de los contadores de la campaña
			var mapStatusCount = {
				'total':		'total',
				'onqueue':		'encola',
				'success':		'conectadas',
				'abandoned':	'abandonadas',
				'pending':		'pendientes',
				'failure':		'fallidas',
				'shortcall':	'cortas',
				'placing':		'marcando',
				'ringing':		'timbrando',
				'noanswer':		'nocontesta',
				'finished':		'terminadas',
				'losttrack':	'sinrastro'
			};
			
			if (respuesta.statuscount != null && respuesta.statuscount.update != null)
			for (var k in respuesta.statuscount.update) {
				if (mapStatusCount[k] != null) this.llamadas.set(
					mapStatusCount[k], respuesta.statuscount.update[k]);
			}
			
			// Lista de las llamadas activas sin agente asignado
			if (respuesta.activecalls != null && respuesta.activecalls.add != null)
			for (var i = 0; i < respuesta.activecalls.add.length; i++) {
				var llamada = respuesta.activecalls.add[i];
				this.llamadasMarcando.addObject(Ember.Object.create({
					callid:		llamada.callid,
					numero:		llamada.callnumber,
					troncal:	llamada.trunk,
					estado:		llamada.callstatus,
					desde:		llamada.desde,
					rtime:		new Date(),
					reciente:	true
				}));
			}
				
			if (respuesta.activecalls != null && respuesta.activecalls.update != null)
			for (var i = 0; i < respuesta.activecalls.update.length; i++) {
				var llamada = respuesta.activecalls.update[i];
				var llamadaMarcando = this.llamadasMarcando.findBy('callid', llamada.callid);
				if (llamadaMarcando != null) llamadaMarcando.setProperties({
					'numero':	llamada.callnumber,
					'troncal':	llamada.trunk,
					'estado':	llamada.callstatus,
					'desde':	llamada.desde,
					'rtime':	new Date(),
					'reciente':	true
				});
			}
			if (respuesta.activecalls != null && respuesta.activecalls.remove != null)
			for (var i = 0; i < respuesta.activecalls.remove.length; i++) {
				var callid = respuesta.activecalls.remove[i].callid;
				for (var j = 0; j < this.llamadasMarcando.length; j++) {
					if (this.llamadasMarcando[j].get('callid') == callid) {
						this.llamadasMarcando.removeAt(j);
					}
				}
			}



			
			
			// Lista de los agentes que atienden llamada
			if (respuesta.agents != null && respuesta.agents.add != null) {
				// Logica para mantener las horas de las ultimas llamadas contestadas de los agentes
				if (count === 0){
					var agentesLastCall = this.agentes;
					var queue = this.get('model') ? this.get('model').get('cola') : null;
					if (paramsType === "outgoing") {
						//console.log("queue_id", params.id_campaign);
						lastCallOutgoing(idCampaign, respuesta.agents, agentesLastCall, queue);
					}
					if (paramsType === "incoming") {
						//console.log("queue_id", params.id_campaign);
						lastCallIncoming(idCampaign, respuesta.agents, agentesLastCall, queue);
					}
					count++;
				}
				for (var i = 0; i < respuesta.agents.add.length; i++) {
					var agente = respuesta.agents.add[i];
					const agentUpdate = agentUpdateColor(agente.status, agente.agent);
					this.agentes.addObject(Ember.Object.create({
						canal:     agente.agent,
						nombre:    agente.name || agente.agent,
						numero:    agente.callnumber,
						troncal:   agente.trunk,
						estado:    agente.status,
						image: 	   Ember.String.htmlSafe(agentUpdate.statusImage),
						desde:     agente.desde,
						rtime:     new Date(),
						reciente:  true
					}));
					agentColor(agente.status, agente.agent);
				}
				// Re-sort agents after adding: offline agents at bottom
				if (respuesta.agents.add.length > 0) {
					this.sortAgentsByStatus();
				}
			}

			// Lista de agentes cuando actualizan sus estados
			if (respuesta.agents != null && respuesta.agents.update != null) {
			    for (var i = 0; i < respuesta.agents.update.length; i++) {
			        var agente = respuesta.agents.update[i];
			        const agentUpdate = agentUpdateColor(agente.status, agente.agent);
			        var agenteLista = this.agentes.findBy('canal', agente.agent);
			        //console.log(agenteLista);
			        if (agenteLista != null) {
			            agenteLista.setProperties({
			                'nombre':   agente.name || agente.agent,
			                'numero':   agente.callnumber,
			                'troncal':  agente.trunk,
			                'estado':   agente.status,
			                'image':    Ember.String.htmlSafe(agentUpdate.statusImage),
			                'desde':    agente.desde,
			                'rtime':    new Date(),
			                'reciente': true
			            });

			            // Removed incorrect logic that changed other agents to "Free" when one becomes "Busy"
			            // Backend handles status updates properly via QueueMemberStatus events
			        }
			    }
			    // Re-sort agents: offline agents at bottom
			    this.sortAgentsByStatus();
			}
			
			// Removed incorrect logic that set all free agents to "ringing" when calls appeared
			// Agent status should only show "ringing" when their phone is actually ringing
			
			// Removed incorrect logic that changed "Ringing" agents to "Free" when calls ended
			// Agent status updates should come from backend, not inferred from call events

			// Removed incorrect logic that set all free agents to "ringing" on page reload
			// Agent status should be determined by backend, not frontend assumptions
			



			// Lista de agentes cuando se desconectan
			if (respuesta.agents != null && respuesta.agents.remove != null)
			for (var i = 0; i < respuesta.agents.remove.length; i++) {
				var agentchannel = respuesta.agents.remove[i].agent;
				for (var j = 0; j < this.agentes.length; j++) {
					if (this.agentes[j].get('canal') == agentchannel) {
						this.agentes.removeAt(j);
					}
				}
			}
			
			// Registro de los eventos de la llamada
			if (respuesta.log != null)
			for (var i = 0; i < respuesta.log.length; i++) {
				var registro = respuesta.log[i];
				this.registro.addObject({
					id:			registro.id,	// <--- id puede ser null en caso de link/unlink
					timestamp:	registro.timestamp,
					mensaje: 	registro.mensaje
				});
			}
			
			// Estadísticas de la campaña
			if (respuesta.stats != null) {
				this.llamadas.set('max_duration', respuesta.stats.update.max_duration);
				this.llamadas.set('total_sec', respuesta.stats.update.total_sec);
			} else if (respuesta.duration != null) {
				var m = this.llamadas.get('max_duration');
				if (m < respuesta.duration)
					this.llamadas.set('max_duration', respuesta.duration);
				this.llamadas.set('total_sec', this.llamadas.get('total_sec') + respuesta.duration);
			}
			
			return true;
		},
		// Sort agents: offline (logged out) agents at the bottom
		sortAgentsByStatus: function() {
			var offlineStatuses = ['Logged out', 'No Logoneado', 'Déconnecté', 'Не в системе', 'Oturumu Kapalı', 'No logon'];
			var self = this;
			var sortedAgents = this.agentes.toArray().sort(function(a, b) {
				var aOffline = offlineStatuses.indexOf(a.get('estado')) !== -1;
				var bOffline = offlineStatuses.indexOf(b.get('estado')) !== -1;
				if (aOffline && !bOffline) return 1;
				if (!aOffline && bOffline) return -1;
				return 0;
			});

			var orderChanged = false;
			if (this.agentes.length !== sortedAgents.length) {
				orderChanged = true;
			} else {
				for (var i = 0; i < sortedAgents.length; i++) {
					if (this.agentes.objectAt(i) !== sortedAgents[i]) {
						orderChanged = true;
						break;
					}
				}
			}

			if (!orderChanged) {
				this.agentes.forEach(function(agent) {
					agentColor(agent.get('estado'), agent.get('canal'));
				});
				return;
			}

			var container = $('.agent-table-wrapper');
			var scrollTop = container.scrollTop();

			this.agentes.clear();
			sortedAgents.forEach(function(agent) {
				self.agentes.pushObject(agent);
				agentColor(agent.get('estado'), agent.get('canal'));
			});

			Ember.run.next(function() {
				container.scrollTop(scrollTop);
			});
		},
		actions: {
			cargarprevios: function() {
				this.cargarprevios();
			}
		},
		cargarprevios: function() {
			var campaign = this.get('model');
			$.get('index.php', {
				menu:			module_name, 
				rawmode:		'yes',
				action:			'loadPreviousLogEntries',
				campaigntype:	campaign.get('type'),
				campaignid:		campaign.get('id_campaign'),
				beforeid:		(this.registro.length > 0) ? this.registro[0].id : null
			}, function(respuesta) {
				verificar_error_session(respuesta);
				if (respuesta.status == 'error') {
					mostrar_mensaje_error(respuesta.message);
					return;
				}
				for (var i = respuesta.log.length - 1; i >= 0; i--) {
					var registro = respuesta.log[i];
					this.registro.insertAt(0, {
						id:			registro.id,
						timestamp:	registro.timestamp,
						mensaje: 	registro.mensaje
					});
				}
			}.bind(this), 'json');
		}
	});

	App.StatLlamadas = Ember.Object.extend({
		// Estados en común para todas las campañas
		total:		0,
		encola:		0,
		conectadas:	0,
		abandonadas:0,
		max_duration:0,
		total_sec:  0,
		fmttime: function(p) {
			var tiempo = [0, 0, 0];
			tiempo[0] = p;
			tiempo[1] = (tiempo[0] - (tiempo[0] % 60)) / 60;
			tiempo[0] %= 60;
			tiempo[2] = (tiempo[1] - (tiempo[1] % 60)) / 60;
			tiempo[1] %= 60;
			var i = 0;
			for (i = 0; i < 3; i++) { if (tiempo[i] <= 9) tiempo[i] = "0" + tiempo[i]; }
			return tiempo[2] + ':' + tiempo[1] + ':' + tiempo[0];
		},
		fmtpromedio: function() {
			var p, s;
			if (this.get('terminadas') > 0)
				p = this.get('total_sec') / this.get('terminadas');
			else if (this.get('conectadas') > 0)
				p = this.get('total_sec') / this.get('conectadas');
			else p = 0;
			p = Math.round(p);
			return this.fmttime(p);
			
		}.property('total_sec', 'terminadas', 'conectadas'),
		fmtmaxduration: function() {
			return this.fmttime(this.get('max_duration'));
		}.property('max_duration'),

		// Estados válidos sólo para campañas salientes
		pendientes:	0,
		marcando:	0,
		timbrando:	0,
		fallidas:	0,
		nocontesta: 0,
		cortas:		0,
		
		// Estados válidos sólo para campañas entrantes
		terminadas: 0,
		sinrastro:	0
	});

	App.RegistroView = Ember.View.extend({
		didInsertElement: function() {
			this.scroll();
		},
		registroChanged: function() {
			var s = this;
			Ember.run.next(function() { s.scroll(); });
		}.observes('context.registro.@each'),
		scroll: function() {
			// Forzar a mostrar el último registro
			var r = this.$();
			r.scrollTop(r.prop('scrollHeight'));
		}
	});

	// Context menu handler for unbreaking/logging in agents
	$(document).on('click', '.agent-table-wrapper table tbody tr', function(event) {
		var agentChannel = $(this).attr('data-agent');
		var agentStatus = $(this).attr('data-status') || '';
		
		if (!agentChannel) return;

		var statusLower = agentStatus.toLowerCase();
		var isPaused = statusLower.indexOf('break') !== -1 || 
		               statusLower.indexOf('descanso') !== -1 || 
		               statusLower.indexOf('pause') !== -1 || 
		               statusLower.indexOf('paused') !== -1;
		
		var isLoggedOut = statusLower.indexOf('no logon') !== -1 || 
		                  statusLower.indexOf('logged out') !== -1 || 
		                  statusLower.indexOf('no logoneado') !== -1;
		
		var hasPaused = statusLower.indexOf('break') !== -1 || 
		                statusLower.indexOf('descanso') !== -1 || 
		                statusLower.indexOf('pause') !== -1 || 
		                statusLower.indexOf('paused') !== -1;
		
		var hasLoggedOut = statusLower.indexOf('no logon') !== -1 || 
		                   statusLower.indexOf('logged out') !== -1 || 
		                   statusLower.indexOf('no logoneado') !== -1;
		
		var hasBusy = statusLower.indexOf('busy') !== -1 || 
		              statusLower.indexOf('ocupado') !== -1 || 
		              statusLower.indexOf('oncall') !== -1 || 
		              statusLower.indexOf('on call') !== -1 || 
		              statusLower.indexOf('occupé') !== -1;

		var hasPhoneOff = statusLower.indexOf('phone off') !== -1 || statusLower.indexOf('phoneoff') !== -1;
		
		if (hasPaused || hasLoggedOut || hasBusy || hasPhoneOff) {
			if (hasPaused) {
				$('#btnUnbreakAgent').show().text('🔓 Finalizar Descanso');
			} else {
				$('#btnUnbreakAgent').hide();
			}
			
			if (hasLoggedOut) {
				$('#btnForceLoginAgent').show().text('🔑 Iniciar Sesión');
			} else {
				$('#btnForceLoginAgent').hide();
			}
			
			if (hasBusy) {
				var callNumberTd = $(this).find('td').eq(2).text().trim();
				if (callNumberTd !== '' && callNumberTd !== '-') {
					$('#btnSpyAgent').show().text('👂 Escuchar Llamada');
				} else {
					$('#btnSpyAgent').hide();
				}
			} else {
				$('#btnSpyAgent').hide();
			}
			
			if (hasPhoneOff) {
				$('#btnReregisterWebphone').show().text('🔄 Re-registrar WebPhone');
			} else {
				$('#btnReregisterWebphone').hide();
			}
			
			$('#agentContextMenu').css({
				top: event.pageY + 'px',
				left: event.pageX + 'px'
			}).fadeIn(150);
			
			$('#agentContextMenu').data('agentChannel', agentChannel);
			event.stopPropagation();
		} else {
			$('#agentContextMenu').fadeOut(100);
		}
	});

	$(document).on('click', function() {
		$('#agentContextMenu').fadeOut(100);
	});

	$(document).on('click', '#btnUnbreakAgent', function(e) {
		e.preventDefault();
		var agentChannel = $('#agentContextMenu').data('agentChannel');
		if (agentChannel) {
			var btn = $(this);
			btn.text('Procesando...');
			
			$.post('index.php', {
				menu: module_name,
				rawmode: 'yes',
				action: 'forceUnbreakAgent',
				agentchannel: agentChannel
			}, function(response) {
				$('#agentContextMenu').fadeOut(100);
				btn.text('🔓 Finalizar Descanso');
				
				if (response.status !== 'success') {
					alert('Error al finalizar descanso: ' + response.message);
				}
			}, 'json');
		}
	});

	$(document).on('click', '#btnForceLoginAgent', function(e) {
		e.preventDefault();
		var agentChannel = $('#agentContextMenu').data('agentChannel');
		if (agentChannel) {
			var btn = $(this);
			btn.text('Procesando...');
			
			$.post('index.php', {
				menu: module_name,
				rawmode: 'yes',
				action: 'forceLoginAgent',
				agentchannel: agentChannel
			}, function(response) {
				$('#agentContextMenu').fadeOut(100);
				btn.text('🔑 Iniciar Sesión');
				
				if (response.status !== 'success') {
					alert('Error al iniciar sesión: ' + response.message);
				}
			}, 'json');
		}
	});

	$(document).on('click', '#btnSpyAgent', function(e) {
		e.preventDefault();
		var agentChannel = $('#agentContextMenu').data('agentChannel');
		if (agentChannel) {
			var btn = $(this);
			btn.text('Conectando...');
			
			$.post('index.php', {
				menu: module_name,
				rawmode: 'yes',
				action: 'spyAgent',
				agentchannel: agentChannel
			}, function(response) {
				$('#agentContextMenu').fadeOut(100);
				btn.text('👂 Escuchar Llamada');
			
				if (response.status !== 'success') {
					alert('Error al escuchar llamada: ' + response.message);
				} else {
					alert('Llamada de escucha iniciada hacia su extensión.');
				}
			}, 'json');
		}
	});

	$(document).on('click', '#btnReregisterWebphone', function(e) {
		e.preventDefault();
		var agentChannel = $('#agentContextMenu').data('agentChannel');
		if (agentChannel) {
			var btn = $(this);
			btn.text('Procesando...');
			
			$.post('index.php', {
				menu: module_name,
				rawmode: 'yes',
				action: 'reregisterWebphone',
				agentchannel: agentChannel
			}, function(response) {
				$('#agentContextMenu').fadeOut(100);
				btn.text('🔄 Re-registrar WebPhone');
				
				if (response.status !== 'success') {
					alert('Error al re-registrar: ' + response.message);
				} else {
					alert('Se envió la señal de re-registro al WebPhone.');
				}
			}, 'json');
		}
	});

});

function mostrar_mensaje_error(s)
{
	$('#issabel-callcenter-error-message-text').text(s);
	$('#issabel-callcenter-error-message').show('slow', 'linear', function() {
		setTimeout(function() {
			$('#issabel-callcenter-error-message').fadeOut();
		}, 5000);
	});
}


function agentColor(status, canal) {
setTimeout(() => {

  if (status.includes('Busy') || status.includes('Ocupado') || status.includes('Occupé') || status.includes('Meşgul') || status.includes('Занят')) {
    color = '#fef7e0'; // Soft pastel yellow/amber
  } else if (status.includes('On break') || status.includes('En descanso') || status.includes('En pause') || status.includes('На перерыве') || status.includes('Molada') || status.includes('descanso')) {
    color = '#fff0e6'; // Soft pastel orange
  } else {
    switch (status) {
      case 'Ringing':
        color = '#e8f0fe'; // Soft light blue
        break;
      case 'Free':
      case 'Libre':
      case 'Свобоden':
      case 'Boşta':
        color = '#e6f4ea'; // Soft pastel green
        break;
      case 'Busy':
      case 'Ocupado':
      case 'Occupé':
      case 'Занят':
      case 'Meşgul':
        color = '#fef7e0'; // Soft pastel yellow/amber
        break;
      case 'Unavailable':
      case 'Logged out':
      case 'No logon':
      case 'Déconnecté':
      case 'Вышел':
      case 'Yok':
        color = '#fce8e6'; // Soft pastel red
        break;
      default:
        color = '#ffffff';
        break;
    }
  }

    const elements = document.getElementsByClassName(canal);
    for (let i = 0; i < elements.length; i++) {
      elements[i].style.backgroundColor = color;
      //console.log(elements.length);
    }
	}, 100);
}

function agentUpdateColor(status, canal) {
  let statusImage;

  if (status.includes('Busy') || status.includes('Ocupado') || status.includes('Occupé') || status.includes('Meşgul') || status.includes('Занят')) {
    color = '#fef7e0'; // Soft pastel yellow/amber
    statusImage = '<img src="/modules/' + module_name + '/images/agent-busy.png" alt="Ocupado" style="padding-right:1px;"/>';
  } else if (status.includes('On break') || status.includes('En descanso') || status.includes('En pause') || status.includes('На перерыве') || status.includes('Molada') || status.includes('descanso')) {
    color = '#fff0e6'; // Soft pastel orange
    statusImage = '<img src="/modules/' + module_name + '/images/agent-break.png" alt="En Break" style="padding-right:1px;"/>';
  } else {
    switch (status) {
      case 'Ringing':
        color = '#e8f0fe'; // Soft light blue
        statusImage = '<img src="/modules/' + module_name + '/images/agent-ringing.gif" alt="Desconectado" style="padding-right:1px;"/>';
        break;
      case 'Free':
      case 'Libre':
      case 'Свобоden':
      case 'Boşta':
        color = '#e6f4ea'; // Soft pastel green
        statusImage = '<img src="/modules/' + module_name + '/images/agent-available.png" alt="Disponible" style="padding-right:1px;"/>';
        break;
      case 'Busy':
      case 'Ocupado':
      case 'Occupé':
      case 'Занят':
      case 'Meşgul':
        color = '#fef7e0'; // Soft pastel yellow/amber
        statusImage = '<img src="/modules/' + module_name + '/images/agent-busy.png" alt="Ocupado" style="padding-right:1px;"/>';
        break;
      case 'Logged out':
      case 'No logon':
      case 'Déconnecté':
      case 'Вышел':
      case 'Yok':
        color = '#fce8e6'; // Soft pastel red
        statusImage = '<img src="/modules/' + module_name + '/images/agent-disconected.png" alt="Desconectado" style="padding-right:1px;"/>';
        break;
      default:
        color = '#ffffff';
        statusImage = '';
        break;
    }
  }

const elements = document.getElementsByClassName(canal);
for (let i = 0; i < elements.length; i++) {
    elements[i].style.backgroundColor = color;
  }
  return { statusImage};
}

function lastCallIncoming(id_campaign, respuesta, agentes, queue) {
    fetch('/modules/' + module_name + '/libs/api.php?id_campaignIncoming=' + id_campaign + '&queue=' + queue)
        .then(response => response.json())
        .then(data => {
        	//console.log(data);
           var listaLastCall = data.listaLastCall;
           var unavailables = data.unavailables;
            for (var i = 0; i < respuesta.add.length; i++) {
                var agente = respuesta.add[i];
                var agenteLista = agentes.findBy('canal', agente.agent);
                var lastCallTime = listaLastCall.find(item => item.agent === agente.agent);
                var unavailableAgent = unavailables.find(item => item.agent === agente.agent);
                //console.log(lastCallTime);
                //console.log(agenteLista);
                var properties = {
			        'reciente': true
			    };
			    if (agenteLista != null) {
			        if (lastCallTime != null) {
			            properties.desde = lastCallTime.lastCall;
			            if (unavailableAgent) {
			                agentColor('Unavailable', agente.agent);
			                properties.estado = "Phone Off";
			            }
			        } else {
			            properties.desde = "No calls";
			            if (unavailableAgent) {
			                agentColor('Unavailable', agente.agent);
			                properties.estado = "Phone Off";
			            }
			        }
			        agenteLista.setProperties(properties);
			    }
            }
        })
        .catch(error => console.error('Error in fetch:', error));
}

function lastCallOutgoing(id_campaign, respuesta, agentes, queue){
	fetch('/modules/' + module_name + '/libs/api.php?id_campaignOutgoing=' + id_campaign + '&queue=' + queue)
        .then(response => response.json())
        .then(data => {
        	//console.log(data);
           var listaLastCall = data.listaLastCall;
           var unavailables = data.unavailables;
            for (var i = 0; i < respuesta.add.length; i++) {
                var agente = respuesta.add[i];
                var agenteLista = agentes.findBy('canal', agente.agent);
                var lastCallTime = listaLastCall.find(item => item.agent === agente.agent);
                var unavailableAgent = unavailables.find(item => item.agent === agente.agent);
                //console.log(lastCallTime);
                //console.log(agenteLista);
                var properties = {
			        'reciente': true
			    };
			    if (agenteLista != null) {
			        if (lastCallTime != null) {
			            properties.desde = lastCallTime.lastCall;
			            if (unavailableAgent) {
			                agentColor('Unavailable', agente.agent);
			                properties.estado = "Phone Off";
			            }
			        } else {
			            properties.desde = "No calls";
			            if (unavailableAgent) {
			                agentColor('Unavailable', agente.agent);
			                properties.estado = "Phone Off";
			            }
			        }
			        agenteLista.setProperties(properties);
			    }
            }
        })
        .catch(error => console.error('Error in fetch:', error));
}