from sqlalchemy import Column, Integer, String, DateTime, func, Boolean, ForeignKey
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
    
    Stores metadata about uploaded programs and their ingestion status.
    
    Relationships:
        - user: User who uploaded this program
        - sources: Data sources that make up this program
    """
    __tablename__ = "programs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String, nullable=False)  # e.g., "MIT Computer Science 2024"
    description = Column(String, nullable=True)
    institution = Column(String, nullable=True)  # e.g., "MIT", "Stanford"
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
    """
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    program_id = Column(Integer, ForeignKey("programs.id"), nullable=False, index=True)
    source_type = Column(String, nullable=False)  # "pdf", "link", "image", "text"
    source_url = Column(String, nullable=True)  # URL for links or file path for uploaded files
    file_name = Column(String, nullable=True)  # Original file name
    status = Column(String, default="pending")  # "pending", "processing", "completed", "failed"
    error_message = Column(String, nullable=True)  # Error details if status is "failed"
    processed_text = Column(String, nullable=True)  # Extracted and chunked text content
    source_metadata = Column(String, nullable=True)  # JSON-formatted metadata
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="sources")
    program = relationship("Program", back_populates="sources")


class Comparison(Base):
    """Comparison model representing a curriculum comparison analysis.
    
    Stores results of comparing two programs and their scoring/diff results.
    
    Relationships:
        - user: User who created this comparison
    """
    __tablename__ = "comparisons"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String, nullable=False)
    program_a_id = Column(Integer, ForeignKey("programs.id"), nullable=True)  # First program in comparison
    program_b_id = Column(Integer, ForeignKey("programs.id"), nullable=True)  # Second program in comparison
    comparison_results = Column(String, nullable=True)  # JSON-formatted comparison results
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="comparisons")
    program_a = relationship("Program", foreign_keys=[program_a_id])
    program_b = relationship("Program", foreign_keys=[program_b_id])