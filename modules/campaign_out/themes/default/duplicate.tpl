<form method="post">
<table width="99%" border="0" cellspacing="0" cellpadding="0" align="center">
{if !$FRAMEWORK_TIENE_TITULO_MODULO}
<tr class="moduleTitle">
  <td class="moduleTitle" valign="middle">&nbsp;&nbsp;<img src="{$icon}" border="0" align="absmiddle" />&nbsp;&nbsp;{$title}</td>
</tr>
{/if}
<tr>
  <td class="duplicate-container">
    <div class="duplicate-card">
      <div class="duplicate-header">
        <h2>{$title}</h2>
        <p class="duplicate-subtitle">Duplicando campaña: <strong class="original-name">{$original_name|escape}</strong></p>
      </div>

      <div class="duplicate-body">
        <div class="form-group">
          <label for="new_name">{$NEW_NAME_LABEL} <span class="required">*</span></label>
          <input type="text" id="new_name" name="new_name" placeholder="Ingrese el nuevo nombre..." required value="{$new_name|escape}" autocomplete="off" />
        </div>
      </div>

      <div class="duplicate-footer">
        <button type="submit" name="save_duplicate" class="btn btn-primary">{$SAVE}</button>
        <button type="submit" name="cancel" class="btn btn-secondary">{$CANCEL}</button>
      </div>
    </div>
  </td>
</tr>
</table>
<input type="hidden" name="id_campaign" value="{$id_campaign}" />
</form>

<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&display=swap');

.duplicate-container {
    padding: 30px 15px;
    font-family: 'Outfit', sans-serif;
    display: flex;
    justify-content: center;
    align-items: center;
}

.duplicate-card {
    background: #ffffff;
    border-radius: 16px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
    width: 100%;
    max-width: 500px;
    padding: 35px;
    border: 1px solid #eaeaea;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.duplicate-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 15px 35px rgba(0, 0, 0, 0.12);
}

.duplicate-header h2 {
    margin: 0 0 10px 0;
    color: #1a1a1a;
    font-size: 24px;
    font-weight: 600;
}

.duplicate-subtitle {
    margin: 0;
    color: #666666;
    font-size: 14px;
    line-height: 1.5;
}

.original-name {
    color: #2b6cb0;
    font-weight: 600;
    background: #ebf8ff;
    padding: 2px 8px;
    border-radius: 4px;
    display: inline-block;
    margin-top: 2px;
}

.duplicate-body {
    margin: 30px 0;
}

.form-group {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.form-group label {
    font-size: 14px;
    font-weight: 500;
    color: #4a5568;
}

.form-group label .required {
    color: #e53e3e;
}

.form-group input {
    width: 100%;
    padding: 12px 16px;
    font-size: 15px;
    border: 2px solid #e2e8f0;
    border-radius: 8px;
    outline: none;
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
    box-sizing: border-box;
    font-family: inherit;
    color: #2d3748;
}

.form-group input:focus {
    border-color: #3182ce;
    box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.15);
}

.duplicate-footer {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
}

.btn {
    padding: 12px 24px;
    font-size: 14px;
    font-weight: 600;
    border-radius: 8px;
    cursor: pointer;
    border: none;
    font-family: inherit;
    transition: all 0.2s ease;
    text-transform: none;
}

.btn-primary {
    background: linear-gradient(135deg, #3182ce 0%, #2b6cb0 100%);
    color: #ffffff;
    box-shadow: 0 4px 6px rgba(49, 130, 206, 0.2);
}

.btn-primary:hover {
    background: linear-gradient(135deg, #4299e1 0%, #3182ce 100%);
    box-shadow: 0 6px 12px rgba(49, 130, 206, 0.3);
    transform: translateY(-1px);
}

.btn-primary:active {
    transform: translateY(0);
}

.btn-secondary {
    background: #edf2f7;
    color: #4a5568;
}

.btn-secondary:hover {
    background: #e2e8f0;
    color: #2d3748;
}
</style>
