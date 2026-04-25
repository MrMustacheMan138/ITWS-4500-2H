from sqlalchemy import Column, Integer, String, DateTime, func, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    """User model for authentication and access control.
    
    Relationships:
        - programs: Programs uploaded by this user
        - comparisons: Comparisons created by this user
        - sources: Data sources uploaded by this user
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    programs = relationship("Program", back_populates="user", cascade="all, delete-orphan")
    comparisons = relationship("Comparison", back_populates="user", cascade="all, delete-orphan")
    sources = relationship("Source", back_populates="user", cascade="all, delete-orphan")


class Program(Base):
    """Program model representing a curriculum/course catalog.
    
    Relationships:
        - user: User who uploaded this program
        - sources: Data sources that make up this program
    """
    __tablename__ = "programs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String, nullable=False)        # e.g. "MIT Computer Science 2024"
    description = Column(String, nullable=True)
    institution = Column(String, nullable=True)  # e.g. "MIT", "Stanford"
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="programs")
    sources = relationship("Source", back_populates="program", cascade="all, delete-orphan")


class Source(Base):
    """Source model representing individual data sources within a program.
    
    Tracks ingested documents (PDFs, links, etc.) and their processing status.
    
    Relationships:
        - user: User who uploaded this source
        - program: Program this source belongs to
        - chunks: Parsed text chunks extracted from this source
    """
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    program_id = Column(Integer, ForeignKey("programs.id"), nullable=False, index=True)
    source_type = Column(String, nullable=False)     # "pdf", "link", "image", "text"
    source_url = Column(String, nullable=True)
    file_name = Column(String, nullable=True)
    status = Column(String, default="pending")       # "pending", "processing", "completed", "failed"
    error_message = Column(String, nullable=True)
    processed_text = Column(Text, nullable=True)     # First 10k chars of extracted text
    source_metadata = Column(String, nullable=True)  # JSON string
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="sources")
    program = relationship("Program", back_populates="sources")
    chunks = relationship("Chunk", back_populates="source", cascade="all, delete-orphan")


class Chunk(Base):
    """Chunk model representing a parsed, section-classified segment of a source.

    Each source is broken into chunks during ingest. Every chunk is:
        - Assigned to a curriculum section (e.g. "core_requirements") via section_rules.py
        - Stored with its page number and type (text or table)
        - Ready for embedding (embedding column is reserved — null until the
          embedding service is wired up, then stored as a JSON float array
          until pgvector migration happens)

    Relationships:
        - source: The source this chunk was extracted from
    """
    __tablename__ = "chunks"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)        # Order within the source
    text = Column(Text, nullable=False)                  # Raw chunk content
    section = Column(String, nullable=True, index=True)  # Section id from section_rules.py
    chunk_type = Column(String, default="text")          # "text" or "table"
    page_number = Column(Integer, nullable=True)         # PDF page number (null for web sources)
    embedding = Column(Text, nullable=True)              # Reserved: JSON float array for now, pgvector later
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    source = relationship("Source", back_populates="chunks")


class Comparison(Base):
    """Comparison model representing a curriculum comparison analysis.
    
    Relationships:
        - user: User who created this comparison
        - program_a / program_b: The two programs being compared
    """
    __tablename__ = "comparisons"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String, nullable=False)
    program_a_id = Column(Integer, ForeignKey("programs.id"), nullable=True)
    program_b_id = Column(Integer, ForeignKey("programs.id"), nullable=True)
    comparison_results = Column(Text, nullable=True)     # JSON string of scores + strengths/weaknesses
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="comparisons")
    program_a = relationship("Program", foreign_keys=[program_a_id])
    program_b = relationship("Program", foreign_keys=[program_b_id])


class ProgramAnalysis(Base):
    __tablename__ = "program_analyses"

    id               = Column(Integer, primary_key=True, index=True)
    program_id       = Column(Integer, ForeignKey("programs.id"), nullable=False, unique=True, index=True)
    overall_score    = Column(Float, nullable=True)
    coverage_pct     = Column(Float, nullable=True)
    missing_sections = Column(JSON, nullable=True)
    score_breakdown  = Column(JSON, nullable=True)
    status           = Column(String, default="pending")  # pending | processing | complete | failed | insufficient
    analyzed_at      = Column(DateTime, nullable=True)
    created_at       = Column(DateTime, server_default=func.now())
    updated_at       = Column(DateTime, server_default=func.now(), onupdate=func.now())

    program          = relationship("Program", back_populates="analysis")
    section_analyses = relationship("SectionAnalysis", back_populates="program_analysis", cascade="all, delete-orphan")


class SectionAnalysis(Base):
    __tablename__ = "section_analyses"

    id                  = Column(Integer, primary_key=True, index=True)
    program_analysis_id = Column(Integer, ForeignKey("program_analyses.id"), nullable=False, index=True)
    section_label       = Column(String, nullable=False)
    score               = Column(Float, nullable=True)
    summary             = Column(Text, nullable=True)
    strengths           = Column(JSON, nullable=True)
    weaknesses          = Column(JSON, nullable=True)
    missing_signals     = Column(JSON, nullable=True)
    confidence          = Column(String, nullable=True)
    insufficient        = Column(Boolean, default=False)
    insufficient_reason = Column(String, nullable=True)
    created_at          = Column(DateTime, server_default=func.now())

    program_analysis = relationship("ProgramAnalysis", back_populates="section_analyses")
