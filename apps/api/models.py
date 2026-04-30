from sqlalchemy import Column, Integer, String, DateTime, func, Boolean, ForeignKey, Text, Float, JSON
from sqlalchemy.orm import relationship 
from pgvector.sqlalchemy import Vector
from database import Base


class User(Base):
    """User model for authentication and access control."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    programs = relationship("Program", back_populates="user", cascade="all, delete-orphan")
    comparisons = relationship("Comparison", back_populates="user", cascade="all, delete-orphan")
    sources = relationship("Source", back_populates="user", cascade="all, delete-orphan")


class Program(Base):
    """Program model representing a curriculum/course catalog."""
    __tablename__ = "programs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    institution = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="programs")
    sources = relationship("Source", back_populates="program", cascade="all, delete-orphan")
    analysis = relationship("ProgramAnalysis", back_populates="program", uselist=False, cascade="all, delete-orphan")


class Source(Base):
    """Source model representing individual data sources within a program."""
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    program_id = Column(Integer, ForeignKey("programs.id"), nullable=False, index=True)
    source_type = Column(String, nullable=False)     # "pdf", "link", "image", "text"
    source_url = Column(String, nullable=True)
    file_name = Column(String, nullable=True)
    status = Column(String, default="pending")       # "pending", "processing", "completed", "failed"
    error_message = Column(String, nullable=True)
    processed_text = Column(Text, nullable=True)
    source_metadata = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="sources")
    program = relationship("Program", back_populates="sources")
    chunks = relationship("Chunk", back_populates="source", cascade="all, delete-orphan")


class Chunk(Base):
    """Chunk model representing a parsed, section-classified segment of a source."""
    __tablename__ = "chunks"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)
    section = Column(String, nullable=True, index=True)
    chunk_type = Column(String, default="text")      # "text" or "table"
    page_number = Column(Integer, nullable=True)
    embedding = Column(Vector(768), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    source = relationship("Source", back_populates="chunks")


class Comparison(Base):
    """Comparison model representing a curriculum comparison analysis."""
    __tablename__ = "comparisons"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String, nullable=False)
    program_a_id = Column(Integer, ForeignKey("programs.id"), nullable=True)
    program_b_id = Column(Integer, ForeignKey("programs.id"), nullable=True)
    comparison_results = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="comparisons")
    program_a = relationship("Program", foreign_keys=[program_a_id])
    program_b = relationship("Program", foreign_keys=[program_b_id])


class ProgramAnalysis(Base):
    __tablename__ = "program_analyses"

    id               = Column(Integer, primary_key=True, index=True)
    program_id       = Column(Integer, ForeignKey("programs.id"), nullable=False, unique=True, index=True)
    overall_score    = Column(Float, nullable=True)
    orientation      = Column(String, nullable=True) # "theory-heavy" | "application-heavy" | "balanced"
    overall_summary  = Column(Text, nullable=True)
    strengths        = Column(JSON, nullable=True)
    weaknesses       = Column(JSON, nullable=True)
    improvements     = Column(JSON, nullable=True)
    score_breakdown  = Column(JSON, nullable=True)
    status           = Column(String, default="pending")
    analyzed_at      = Column(DateTime, nullable=True)
    created_at       = Column(DateTime, server_default=func.now())
    updated_at       = Column(DateTime, server_default=func.now(), onupdate=func.now())

    program          = relationship("Program", back_populates="analysis")

