import os
from typing import Optional
from msgraph import GraphServiceClient
from azure.identity import ClientSecretCredential
import asyncio

class TeamsService:
    def __init__(self):
        self.tenant_id = os.getenv("AZURE_TENANT_ID")
        self.client_id = os.getenv("AZURE_CLIENT_ID")
        self.client_secret = os.getenv("AZURE_CLIENT_SECRET")
        self.teams_channel_id = os.getenv("TEAMS_CHANNEL_ID")
        self.teams_team_id = os.getenv("TEAMS_TEAM_ID")
        
        if all([self.tenant_id, self.client_id, self.client_secret]):
            credential = ClientSecretCredential(
                tenant_id=self.tenant_id,
                client_id=self.client_id,
                client_secret=self.client_secret
            )
            self.client = GraphServiceClient(
                credentials=credential,
                scopes=['https://graph.microsoft.com/.default']
            )
        else:
            self.client = None
            print("Teams integration not configured - missing Azure credentials")
    
    async def send_alert(self, message: str, subject: str = "SmartEmails Alert"):
        """Send an alert message to Teams channel"""
        if not self.client:
            print(f"Teams integration not configured. Alert: {subject} - {message}")
            return
        
        try:
            from msgraph.generated.teams.item.channels.item.messages.messages_request_builder import MessagesRequestBuilder
            from msgraph.generated.models.chat_message import ChatMessage
            from msgraph.generated.models.item_body import ItemBody
            from msgraph.generated.models.body_type import BodyType
            
            chat_message = ChatMessage()
            chat_message.body = ItemBody()
            chat_message.body.content_type = BodyType.Html
            chat_message.body.content = f"<h3>{subject}</h3><p>{message}</p>"
            
            await self.client.teams.by_team_id(self.teams_team_id).channels.by_channel_id(
                self.teams_channel_id
            ).messages.post(chat_message)
            
            print(f"Teams alert sent successfully: {subject}")
        except Exception as e:
            print(f"Failed to send Teams alert: {str(e)}")
    
    async def send_content_not_available_alert(
        self, 
        domain: str, 
        from_email: str, 
        subject_text: str,
        missing_subject: str
    ):
        """Send alert for content not available - matching Power Automate flow"""
        message = f"""
        ❓ Falta conteúdo para responder de forma correta a um email:<br/>
        <strong>{missing_subject}</strong><br/>
        Caso a pergunta seja pertinente, adicionar este conteúdo no Knowledge Base.<br/>
        <br/>
        <strong>Detalhes:</strong><br/>
        Domain: {domain}<br/>
        From: {from_email}<br/>
        Email Subject: {subject_text}
        """
        await self.send_alert(message, "SmartEmails - Content Not Available")
    
    async def send_function_not_implemented_alert(
        self,
        domain: str,
        from_email: str,
        subject: str,
        function_name: str
    ):
        """Send alert for unimplemented function - matching Power Automate flow"""
        message = f"""
        ERRO SMARTEMAILS API: {domain}.<br/>
        No email de {from_email}, com o assunto: {subject}, 
        foi chamada a função <strong>{function_name}</strong> que não está implementada!
        """
        await self.send_alert(message, "SmartEmails - Function Not Implemented")
