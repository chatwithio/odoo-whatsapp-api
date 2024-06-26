# odoo-whatsapp-api
Odoo WhatsApp 360 Dialog Integration
<h2> Description</h2>
This module allows to send messages in any Odoo model. The messages can be from pre-loaded templates of the 360 Dialog namespace or manually writen if the conversation has already been started.
If the message fails, and activity will be created in order to correct the issue.<br/>
This module was tested in v15, v16 and v17.

<h2>Requirements</h2>
To use this module you need to have an authorized API key. You can request one  <a href="https://services.tochat.be/es/whatsapp-business-directory/877b04a9-edb7-45cf-893c-8c9a44fa0bad" target="_blank"><span>here.</span></a>
 <br/><br/>
For development purposes there is a Sandbox environment, in which you can get a free API key to send unlimited WhatsApp Messages to your own phone Number. <br/>
This module allows to send messages using the development environment. Check out the <a href="https://docs.360dialog.com/docs/waba-messaging/sandbox" target="_blank"><span>sandbox docs</span></a>
 <span> to get you free API key</span><br/>

<h2>Installation</h2>
<span>
1. Download or clone the repository and put it in any folder of your Odoo addons path.<br/>
<br/>
2. Configure module dependencies. This module allows to send messages in any model of Odoo. That means you can send WhatsApp messages in your leads, opportunities, purchases, sales, invoices or any other document you are managing. By default the WhatsApp messages are set only in the CRM module. You can change this in the `__manifest__.py` file located in the main directory.
<br/>
<br/>


![dependencies_conf](https://github.com/chatwithio/odoo-whatsapp-api/assets/89967182/26c1bd3f-e973-4e8e-ba4e-0b733b81d1f7)

 
 
 
<br/>
3. Install the module. Start your Odoo server, go to the Apps menú and search for the module. Note: clean the search bar default filters. If the module does not appear, you can try clicking the "Update Apps List" located in the upper menu bar (with the <a href="https://www.odoo.com/documentation/17.0/applications/general/developer_mode.html#:~:text=Open%20the%20command%20palette%20by,with%20assets%20or%20deactivate%20it.&text=The%20Odoo%20Debug%20browser%20extension,Store%20and%20Firefox%20Add%2Dons." target="_blank"> odoo developer mode <a/> activated) or review in the odoo.conf the addons path. 
 <br/>
<br/>

 
 ![install_module](https://github.com/chatwithio/odoo-whatsapp-api/assets/89967182/0dae197e-e24d-40c8-bf39-6111deb8b0f0)

 https://github.com/chatwithio/odoo-whatsapp-api/tree/main/static/description/install_module.jpeg

<span/>
<h2>Configuration</h2>
To start sending messages, there are some issues to consider after installing the module:

<h4>Connection Settings</h4>

Go to the Settings menu, select the WhatsApp section and fill the configuration settings.<br/>
**API KEY**: add in the general config settings the company API-KEY. For Sandbox Api keys activate the Developer Mode. 
<br/>
<br/>
**NAMESPACE**: add in the general config settings the company namespace. For developer environment use  `c8ae5f90_307a_ca4c_b8f6_d1e2a2573574`.
<br/>
<br/>
**WEBHOOK ADDRESS** : the module needs the webhook connection to work properly. Every API key has its own unique WebHook configuration, so make sure it is not used for other developments. Complete the server url considering this example `https://your-odoo-domain.com`.
The module sets the webhook url with the configured url followed by `/api/v1/whatsapp/webhook`<br/>
For developer environment you can use free API development tools like POSTMAN requesting `http://localhost:8069/api/v1/whatsapp/webhook`
<br/>
<br/>

![WhatsApp Image 2024-06-01 at 13 21 57](https://github.com/chatwithio/odoo-whatsapp-api/assets/89967182/d0b2c8b9-9457-4206-83f4-87bcec152808)


 <h4><u>Other Settings</u></h4>
**SET WEBHOOK**: once you complete the webhook url you have to set that connection clicking the Menu `WhatsApp > Configuration > Set Webhook`
<br/>
<br/>

![set_webhook](https://github.com/chatwithio/odoo-whatsapp-api/assets/89967182/68649f41-0447-4fc6-921f-9bcf0f9bdfd8)

<br/>
<br/>
**MODEL ADAPTATION**: this module allows to send whatsapp messages for any model that is subscribed to the mail and activity native features. For each model you have to add a configuration going to the menu `WhatsApp > Configuration > Model Adaptation`
<br/>
In order to send messages for a particular model, a model adaptation configuration needs to be added. For each model, you have to define:
<br/>
→ Message Error Activity Configuration: who is going to receive the activity notification when a message has failed. You can add a specific user or any user field of the model. If both fields are set, the Default User is taken into account only if the User field is not set.
<br/>
→ Phone Number Fields: define from witch fields contains the phone number information. You can select `res.partner` fields. If multiple fields are set, the `res.partner` fields have priority, looking first in the partner's `mobile` and if it's not set in `phone`<br/>
By default the module has preloaded an example of configuration for `crm.lead` model:
<br/>
<br/>

![model_adaptation](https://github.com/chatwithio/odoo-whatsapp-api/assets/89967182/978df6bd-6f09-4546-a98a-4c2925d9a337)

https://github.com/chatwithio/odoo-whatsapp-api/tree/main/static/description/model_adaptation.png

<br/>
<br/>
**MESSAGE TEMPLATES**: the 360 Dialog Templates of your Namespace can be managed in the menu `WhatsApp > Configuration > Message Templates`. Make sure to set up properly the 360 Dialog Reference and the language.<br/>
For templates that uses params, you have to configure the content of them. Each param variable is going to be replaced in the content in the '[]' space. <br/>
The variable params can be either custom plain text or filled with any model field (only char and many2one fields).<br/>
For developer purposes check out the <a href="https://docs.360dialog.com/docs/waba-messaging/sandbox#id-5.-send-a-template-message-optional">Sandbox available templates.<a/><br/>
Here is an example of the `first_welcome_messsage` template:
<br/>
<br/>

![message_template](https://github.com/chatwithio/odoo-whatsapp-api/assets/89967182/7e260482-3c8a-4fe8-b1f1-7f7522919cee)

https://github.com/chatwithio/odoo-whatsapp-api/tree/main/static/description/message_template.png

<br/>
<h2>Usage</h2>
This module modifies two native Odoo features:
<br/>
→ **Mail Compose Wizard**: every odoo model subscribed to the `mail` features, can send an email with the mail compose wizard.
In this form you can find an WhatsApp Checkbox to change the functionality to send a WhatsApp Message instead an email.
<br/>
<br/>

![send_message](https://github.com/chatwithio/odoo-whatsapp-api/assets/89967182/4a046045-c174-45d0-a364-2d886d01ef08)

https://github.com/chatwithio/odoo-whatsapp-api/tree/main/static/description/send_message.png

<br/>
→ **Message Post With Template**: massive emailing can use this method to send a predefine template. The mail templates have a configuration that links that template with a 360 Dialog Template. When a message is post with a Mail Template related to a WhatsApp template the mail is replaced with a WhatsApp message. 
This is used by the Mail Automation module.
<br/>
<br/>

![email_template](https://github.com/chatwithio/odoo-whatsapp-api/assets/89967182/37144f97-8efa-4865-b010-d5354cb1a529)

https://github.com/chatwithio/odoo-whatsapp-api/tree/main/static/description/email_template.png

<h2>Technical Support</h2>
Contact: info@chatwith.io
