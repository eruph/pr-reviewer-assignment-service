from fastapi import APIRouter

from .team.router import router as team_router
from .users.router import router as users_router
from .pull_requests.router import router as pr_router
from .stats.router import router as stats_router

router = APIRouter()

router.include_router(team_router)
router.include_router(users_router)
router.include_router(pr_router)
router.include_router(stats_router)
