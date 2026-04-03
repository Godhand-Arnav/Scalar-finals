"""
Tasks package — procedurally generated misinformation investigation scenarios.
v2.0: Added PolitifactTask (LIAR dataset), ImageForensicsTask, SECFraudTask.
"""
from env.tasks.task_base import BaseTask
from env.tasks.task_fabricated_stats import FabricatedStatsTask
from env.tasks.task_out_of_context import OutOfContextTask
from env.tasks.task_coordinated_campaign import CoordinatedCampaignTask
from env.tasks.task_politifact import PolitifactTask
from env.tasks.task_image_forensics import ImageForensicsTask
from env.tasks.task_sec_fraud import SECFraudTask

TASK_REGISTRY = {
    "fabricated_stats":      FabricatedStatsTask,
    "out_of_context":        OutOfContextTask,
    "coordinated_campaign":  CoordinatedCampaignTask,
    "politifact_liar":       PolitifactTask,
    "image_forensics":       ImageForensicsTask,
    "sec_fraud":             SECFraudTask,
}

__all__ = [
    "BaseTask",
    "FabricatedStatsTask",
    "OutOfContextTask",
    "CoordinatedCampaignTask",
    "PolitifactTask",
    "ImageForensicsTask",
    "SECFraudTask",
    "TASK_REGISTRY",
]
