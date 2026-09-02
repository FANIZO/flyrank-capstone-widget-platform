from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import get_current_owner
from app.config import settings
from app.database import get_db
from app.models import Owner, Widget
from app.schemas import PublicWidgetConfig, WidgetCreate, WidgetResponse, WidgetUpdate


router = APIRouter(tags=["Widgets"])


def owned_widget(database: Session, widget_id: int, owner_id: int) -> Widget:
    widget = database.scalar(
        select(Widget).where(Widget.id == widget_id, Widget.owner_id == owner_id)
    )
    if widget is None:
        raise HTTPException(status_code=404, detail="Widget not found")
    return widget


@router.post("/widgets", response_model=WidgetResponse, status_code=status.HTTP_201_CREATED)
def create_widget(
    payload: WidgetCreate,
    owner: Owner = Depends(get_current_owner),
    database: Session = Depends(get_db),
):
    widget = Widget(owner_id=owner.id, **payload.model_dump(mode="json"))
    database.add(widget)
    database.commit()
    database.refresh(widget)
    return widget


@router.get("/widgets", response_model=list[WidgetResponse])
def list_widgets(
    owner: Owner = Depends(get_current_owner),
    database: Session = Depends(get_db),
):
    return list(database.scalars(select(Widget).where(Widget.owner_id == owner.id).order_by(Widget.id)))


@router.get("/widgets/{widget_id}", response_model=WidgetResponse)
def get_widget(
    widget_id: int,
    owner: Owner = Depends(get_current_owner),
    database: Session = Depends(get_db),
):
    return owned_widget(database, widget_id, owner.id)


@router.patch("/widgets/{widget_id}", response_model=WidgetResponse)
def update_widget(
    widget_id: int,
    payload: WidgetUpdate,
    owner: Owner = Depends(get_current_owner),
    database: Session = Depends(get_db),
):
    widget = owned_widget(database, widget_id, owner.id)
    for field, value in payload.model_dump(exclude_unset=True, mode="json").items():
        setattr(widget, field, value)
    database.commit()
    database.refresh(widget)
    return widget


@router.delete("/widgets/{widget_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_widget(
    widget_id: int,
    owner: Owner = Depends(get_current_owner),
    database: Session = Depends(get_db),
):
    database.delete(owned_widget(database, widget_id, owner.id))
    database.commit()
    return Response(status_code=204)


@router.get("/widgets/{widget_id}/snippet")
def widget_snippet(
    widget_id: int,
    owner: Owner = Depends(get_current_owner),
    database: Session = Depends(get_db),
):
    widget = owned_widget(database, widget_id, owner.id)
    source = f"{settings.public_base_url}/assets/widget.v1.js?id={widget.public_id}"
    return {"snippet": f'<script src="{source}"></script>'}


@router.get("/public/widgets/{public_id}/config", response_model=PublicWidgetConfig)
def public_widget_config(public_id: str, response: Response, database: Session = Depends(get_db)):
    widget = database.scalar(select(Widget).where(Widget.public_id == public_id, Widget.active.is_(True)))
    if widget is None:
        raise HTTPException(status_code=404, detail="Widget not found")
    response.headers["Cache-Control"] = "public, max-age=60"
    return PublicWidgetConfig(
        public_id=widget.public_id,
        widget_type=widget.widget_type,
        title=widget.title,
        description=widget.description,
        button_text=widget.button_text,
        fields=widget.field_configuration,
        display_options=widget.display_options,
        submission_url=f"{settings.public_base_url}/public/widgets/{widget.public_id}/submissions",
    )
