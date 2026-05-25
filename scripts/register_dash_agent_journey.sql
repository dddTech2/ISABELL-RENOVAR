-- Queries to execute on the Issabel SQLite menu database (usually located at /var/www/db/menu.db)

INSERT INTO menu (id, id_menu, description, type) VALUES ('dash_agent_journey', 'reports', 'Dash Agent Journey', 'module');

-- Make sure to give permissions to the administrator and coordinator groups
-- The group ID for administrator is usually 1, and for coordinator is usually 3 or similar.
-- You should verify the group IDs in the acl_group table.
-- Assuming admin is 1 and coordinator is 3:

INSERT INTO acl_group_permission (id_action, id_group) 
SELECT id, 1 FROM acl_action WHERE name = 'dash_agent_journey';

INSERT INTO acl_group_permission (id_action, id_group) 
SELECT id, 3 FROM acl_action WHERE name = 'dash_agent_journey';

-- Note: the exact acl structure depends on Issabel's acl.db.
-- A safe way to grant permissions is through the web interface (System -> Users -> Group Permissions).
-- Once the menu is inserted in menu.db, you can go to the Issabel web interface to grant the group permissions.
