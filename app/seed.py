from sqlalchemy import select

from app.auth import hash_password
from app.config import settings
from app.database import Base, SessionLocal, engine
from app.models import Owner, Widget
from app.schemas import DEFAULT_FIELDS


def seed():
    Base.metadata.create_all(bind=engine)
    database = SessionLocal()
    try:
        owner = database.scalar(select(Owner).where(Owner.email == "demo@example.com"))
        if owner is None:
            owner = Owner(email="demo@example.com", password_hash=hash_password("DemoPassword123!"))
            database.add(owner)
            database.flush()
        widget = database.scalar(select(Widget).where(Widget.owner_id == owner.id))
        if widget is None:
            widget = Widget(
                owner_id=owner.id,
                title="Contact our team",
                description="Send us a message and we will respond soon.",
                button_text="Send message",
                widget_type="contact",
                field_configuration=DEFAULT_FIELDS,
                display_options={"theme": "light"},
            )
            database.add(widget)
        database.commit()
        database.refresh(widget)
        print("Demo owner: demo@example.com / DemoPassword123!")
        print(f"Public widget id: {widget.public_id}")
        print(f'<script src="{settings.public_base_url}/assets/widget.v1.js?id={widget.public_id}"></script>')
    finally:
        database.close()


if __name__ == "__main__":
    seed()
