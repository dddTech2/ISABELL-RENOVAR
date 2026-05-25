import os
import shutil

source_module = "c:/Users/dazad/Documents/ISABELL-RENOVAR/modules/agent_journey"
dest_module = "c:/Users/dazad/Documents/ISABELL-RENOVAR/modules/dash_agent_journey"

# 1. Copy the directory
if os.path.exists(dest_module):
    shutil.rmtree(dest_module)
shutil.copytree(source_module, dest_module)

# 2. Modify index.php
index_path = os.path.join(dest_module, "index.php")
with open(index_path, "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("agent_journey", "dash_agent_journey")
content = content.replace("paloSantoAgentJourney", "paloSantoDashAgentJourney")

# We will handle the getMetrics function later with replace_file_content or multi_replace_file_content
# For now, just save the renamed basic setup.
with open(index_path, "w", encoding="utf-8") as f:
    f.write(content)

# 3. Rename and modify the class file
libs_dir = os.path.join(dest_module, "libs")
old_class = os.path.join(libs_dir, "paloSantoAgentJourney.class.php")
new_class = os.path.join(libs_dir, "paloSantoDashAgentJourney.class.php")

if os.path.exists(old_class):
    os.rename(old_class, new_class)

with open(new_class, "r", encoding="utf-8") as f:
    class_content = f.read()

class_content = class_content.replace("paloSantoAgentJourney", "paloSantoDashAgentJourney")
class_content = class_content.replace("AgentJourney", "DashAgentJourney")

with open(new_class, "w", encoding="utf-8") as f:
    f.write(class_content)

print("Module copied and renamed successfully.")
