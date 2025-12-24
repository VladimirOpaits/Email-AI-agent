from apps.email_classifier.celery_app import celery_app
from core.logger import logger
from core.graph.app_state import GraphState

@celery_app.task(
    name="process_email_task",
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    max_retries=5,
    retry_jitter=True,
)
def process_email_task(self, email_data_dict):
    try:
        from core.services.models import EmailData
        email = EmailData(**email_data_dict)

        logger.info(f"Starting processing for email ID: {email.id}")

        initial_state = GraphState(
            email=email,
            classification_result=None,
            client_id=None,
            client_name_db=None,
            new_claim=None,
            next_step="classify"
        )
        
        from core.graph.blueprint import app
        app.invoke(initial_state)

        logger.info(f"Finished processing for email ID: {email.id}")

    except Exception as e:
        logger.error(f"Error in task {self.request.id} (Attempt {self.request.retries}): {e}")
        raise e