from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///youtube_stats.db"
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class ChannelStats(Base):
    __tablename__ = 'channel_stats'
    id = Column(Integer, primary_key=True, index=True)
    channel_id = Column(String, index=True)
    name = Column(String)
    subscribers = Column(Integer)
    views = Column(Integer)
    videos = Column(Integer)
    likes = Column(Integer)
    comments = Column(Integer)
    category = Column(String) 
    country = Column(String)

def init_db():
    Base.metadata.create_all(bind=engine)

def save_channel_stats(channel_id, name, subs, views, videos, likes, comments, category, country):
    db = SessionLocal()

    last_record = db.query(ChannelStats).filter(
        ChannelStats.channel_id == channel_id
    ).order_by(ChannelStats.id.desc()).first()

    daily_change = 0
    if last_record:
        daily_change = subs - last_record.subscribers

    stats = ChannelStats(
        channel_id=channel_id,
        name=name,
        subscribers=subs,
        views=views,
        videos=videos,
        likes=likes,
        comments=comments,
        category=category,
        country =country,
    )

    db.add(stats)
    db.commit()
    db.close()

