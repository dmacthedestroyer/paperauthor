from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

Base = declarative_base()


class Author(Base):
    __tablename__ = "author"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    affiliation = Column(String)


class Paper(Base):
    __tablename__ = "paper"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    year = Column(Integer)
    conferenceid = Column(Integer, ForeignKey('conference.id'))
    conference = relationship("Conference")
    journalid = Column(Integer, ForeignKey('journal.id'))
    journal = relationship("Journal")
    keyword = Column(String)


class PaperAuthor(Base):
    __tablename__ = "paperauthor"

    paperid = Column(Integer, ForeignKey('paper.id'), primary_key=True)
    authorid = Column(Integer, ForeignKey('author.id'), primary_key=True)
    name = Column(String, primary_key=True)
    affiliation = Column(String, primary_key=True)

    paper = relationship("Paper", backref=backref("paperauthors"))
    author = relationship("Author", backref=backref("authorpapers"))


class Journal(Base):
    __tablename__ = "journal"

    id = Column(Integer, primary_key=True)
    shortname = Column(String)
    fullname = Column(String)
    homepage = Column(String)


class Conference(Base):
    __tablename__ = "conference"

    id = Column(Integer, primary_key=True)
    shortname = Column(String)
    fullname = Column(String)
    homepage = Column(String)
