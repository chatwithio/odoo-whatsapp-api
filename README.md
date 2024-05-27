# odoo-whatsapp-api
<h2> Description<h2/>
Odoo WhatsApp 360 Dialog Integration. This module allows to send template messages and custom messages to customer.
If the message fails, and activity will be created in order to correct the issue.
<h2>Configuration<h2/>
To use this module, there are some issues to consider:
<br/>
<br/>
1. API KEY: add in the general config settings the company API-KEY.
<br/>
<br/>
2. NAMESPACE:  add in the general config settings the company namespace. The namespace has the different message templates
<br/>
<br/>
3. WEBHOOK: the system needs the webhook connection to work properly. In Odoo the webhook listener is configured in the odoo url with this extension /api/v1/whatsapp/webhook. The Odoo http Adress has to be added in the general config settings, and then go to WhatsApp > Configurations > Set Webhook. This is going to change the 360 Dialog Webhook Configuration, so make sure it is not used for other developments. 
<br/>
<br/>
4. MODEL ADAPTATION AND DEPENDENCIES: this module allows to send whatsapp messages for any model that is subscribed to the mail and activity native features. To work properly, the module needs two requirements:
<br/>
--> Model Dependencies: the manifest must have Odoo module dependencies where the models are created. For example, if you want to send WhatsApp messages in Purchase Orders, you have to add the 'puchase' module as a dependency.
<br/>
--> Add Model Adaptation: in order to send messages for a particular model, a model adaptation configuration needs to be added. For each model, you have to define:
<br/>
    1. Message Error Activity Configuration: who is going to receive the activity notification when a message has failed
<br/>
    2. Phone Number Fields: define from wich field is going to get the phone number. You can select res.partner fields.  
<br/>
<br/>
5. DEVELOPER MODE: in the general config section the developer mode can be activated, changing the endpoints url to the Sandbox environment
<br/>
<br/>
6. MESSAGE TEMPLATES: the 360 Dialog Templates can be managed from WhatsApp>Configuration>Message Templates. Make sure to set up properly the 360 Dialog Reference and the language. The variables different variables are set and are going to be replaced in the content in the '[]' space.
<br/>
<br/>
6. SENDING MESSAGES: this module modifies two native features:
<br/>
--> Mail Compose Wizard: adds WhatsApp Boolean field to change the wizard functionality to send a WhatsApp Message and not an email.
<br/>
--> Message Post With Template: the mail templates have a configuration that links that template with a 360 Dialog Template. When a message is post with a Wa Template the mail is replaced with a WhatsApp message. This is used by the Mail Automation module.
<h2>Technical Support<h2/>
Developer contact: apelsantiago@gmail.com