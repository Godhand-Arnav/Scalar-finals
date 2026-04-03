"""
Tasks package — procedurally generated misinformation investigation scenarios.
"""
from env.tasks.task_base import BaseTask
from env.tasks.task_fabricated_stats import FabricatedStatsTask
from env.tasks.task_out_of_context import OutOfContextTask
from env.tasks.task_coordinated_campaign import CoordinatedCampaignTask

TASK_REGISTRY = {
    "fabricated_stats": FabricatedStatsTask,
    "out_of_context": OutOfContextTask,
    "coordinated_campaign": CoordinatedCampaignTask,
}

__all__ = [
    "BaseTask", "FabricatedStatsTask", "OutOfContextTask",
    "CoordinatedCampaignTask", "TASK_REGISTRY",
]
