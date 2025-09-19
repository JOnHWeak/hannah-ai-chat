from database import SessionLocal
from models import ChatHistory


def main() -> None:
    session = SessionLocal()
    try:
        item = ChatHistory(
            user_id="test-user",
            session_id="seed",
            question="Xin chào, hôm nay thời tiết thế nào?",
            answer="Xin chào! Tôi là mô hình nội bộ. Đây là câu trả lời mẫu.",
            rating=5,
        )
        session.add(item)
        session.commit()
        print("Inserted ChatHistory id=", item.id)
    finally:
        session.close()


if __name__ == "__main__":
    main()


