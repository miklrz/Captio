from .database import bool_from_db, segments_from_db
from .pydantic_models import TaskPublic, UserPublic, VideoJobPublic


USER_RIGHTS = {
    "user": ["can_generate_subtitles", "can_view_history", "can_manage_own_tasks"],
    "admin": [
        "can_generate_subtitles",
        "can_view_history",
        "can_manage_own_tasks",
        "can_manage_users",
        "can_manage_all_tasks",
        "can_view_all_jobs",
    ],
}


def serialize_user(row: dict) -> UserPublic:
    role = row["role"]
    return UserPublic(
        id=row["id"],
        name=row["name"],
        login=row["login"],
        role=role,
        roles=[role],
        rights=USER_RIGHTS.get(role, []),
        created_at=row.get("created_at"),
    )


def serialize_task(row: dict) -> TaskPublic:
    return TaskPublic(
        id=row["id"],
        title=row["title"],
        done=bool_from_db(row["done"]),
        user_id=row["user_id"],
        created_at=row.get("created_at"),
        updated_at=row.get("updated_at"),
        owner_name=row.get("owner_name"),
        owner_login=row.get("owner_login"),
    )


def serialize_video_job(row: dict) -> VideoJobPublic:
    return VideoJobPublic(
        id=row["id"],
        user_id=row.get("user_id"),
        source_url=row["source_url"],
        source_type=row["source_type"],
        status=row["status"],
        task_mode=row["task_mode"],
        language=row.get("language"),
        target_language=row.get("target_language"),
        text=row.get("transcript_text"),
        segments=segments_from_db(row.get("segments_json")),
        srt_url=f"/api/videos/{row['id']}/srt" if row.get("srt_path") else None,
        error_message=row.get("error_message"),
        created_at=row.get("created_at"),
        updated_at=row.get("updated_at"),
        finished_at=row.get("finished_at"),
    )
