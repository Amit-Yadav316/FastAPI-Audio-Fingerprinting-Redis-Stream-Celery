from sqlalchemy import Column, Integer, String, ForeignKey, JSON
from sqlalchemy.orm import relationship
from database.database import Base

class Song(Base):
    __tablename__ = "songs"  

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    spotify_data = Column(JSON, nullable=True)
    youtube_data = Column(JSON, nullable=True)

    fingerprints = relationship("Fingerprint", back_populates="song")


class Fingerprint(Base):
    __tablename__ = "fingerprints"  

    id = Column(Integer, primary_key=True, index=True)
    hash = Column(String, index=True)
    offset = Column(Integer, index=True)
    song_id = Column(Integer, ForeignKey("songs.id"))  

    song = relationship("Song", back_populates="fingerprints")