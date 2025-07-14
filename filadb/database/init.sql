-- FilaDB Database Schema
-- Initial database setup for FilaDB

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table for multi-user support
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'user' CHECK (role IN ('admin', 'user', 'viewer')),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Manufacturers table
CREATE TABLE manufacturers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) UNIQUE NOT NULL,
    website VARCHAR(500),
    logo_url VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Materials table
CREATE TABLE materials (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) UNIQUE NOT NULL,
    density DECIMAL(5,3) NOT NULL, -- g/cm³
    extruder_temp_min INTEGER,
    extruder_temp_max INTEGER,
    bed_temp_min INTEGER,
    bed_temp_max INTEGER,
    properties JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Filaments table (from SpoolmanDB integration)
CREATE TABLE filaments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    manufacturer_id UUID REFERENCES manufacturers(id) ON DELETE CASCADE,
    material_id UUID REFERENCES materials(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    density DECIMAL(5,3),
    extruder_temp_min INTEGER,
    extruder_temp_max INTEGER,
    bed_temp_min INTEGER,
    bed_temp_max INTEGER,
    colors JSONB DEFAULT '[]', -- Array of color objects
    weights JSONB DEFAULT '[]', -- Array of weight options
    diameters JSONB DEFAULT '[]', -- Array of diameter options
    settings JSONB DEFAULT '{}', -- Additional settings
    spoolman_db_id VARCHAR(255), -- Reference to SpoolmanDB
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(manufacturer_id, name)
);

-- Printers table
CREATE TABLE printers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    type VARCHAR(100),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    status VARCHAR(50) DEFAULT 'offline' CHECK (status IN ('online', 'offline', 'printing', 'paused', 'error')),
    location VARCHAR(255),
    notes TEXT,
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Spools table (individual spool instances)
CREATE TABLE spools (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    filament_id UUID REFERENCES filaments(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    printer_id UUID REFERENCES printers(id) ON DELETE SET NULL,
    weight DECIMAL(8,2) NOT NULL, -- Total weight in grams
    remaining_weight DECIMAL(8,2) NOT NULL, -- Remaining weight in grams
    spool_weight DECIMAL(8,2), -- Empty spool weight in grams
    color VARCHAR(100),
    hex_color VARCHAR(7), -- Hex color code
    diameter DECIMAL(4,2) NOT NULL, -- Diameter in mm
    purchase_date DATE,
    purchase_price DECIMAL(10,2),
    location VARCHAR(255),
    nfc_tag_id VARCHAR(255) UNIQUE,
    qr_code VARCHAR(255) UNIQUE,
    notes TEXT,
    custom_fields JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Print jobs table
CREATE TABLE print_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    printer_id UUID REFERENCES printers(id) ON DELETE CASCADE,
    spool_id UUID REFERENCES spools(id) ON DELETE SET NULL,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    job_name VARCHAR(255),
    start_time TIMESTAMP WITH TIME ZONE,
    end_time TIMESTAMP WITH TIME ZONE,
    filament_used DECIMAL(8,2), -- Filament used in grams
    status VARCHAR(50) DEFAULT 'queued' CHECK (status IN ('queued', 'printing', 'completed', 'failed', 'cancelled')),
    notes TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Activity logs table
CREATE TABLE activity_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    resource_id UUID,
    details JSONB DEFAULT '{}',
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for better performance
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_spools_user_id ON spools(user_id);
CREATE INDEX idx_spools_filament_id ON spools(filament_id);
CREATE INDEX idx_spools_printer_id ON spools(printer_id);
CREATE INDEX idx_spools_nfc_tag_id ON spools(nfc_tag_id);
CREATE INDEX idx_print_jobs_printer_id ON print_jobs(printer_id);
CREATE INDEX idx_print_jobs_spool_id ON print_jobs(spool_id);
CREATE INDEX idx_print_jobs_user_id ON print_jobs(user_id);
CREATE INDEX idx_activity_logs_user_id ON activity_logs(user_id);
CREATE INDEX idx_activity_logs_created_at ON activity_logs(created_at);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers to automatically update updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_manufacturers_updated_at BEFORE UPDATE ON manufacturers FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_materials_updated_at BEFORE UPDATE ON materials FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_filaments_updated_at BEFORE UPDATE ON filaments FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_printers_updated_at BEFORE UPDATE ON printers FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_spools_updated_at BEFORE UPDATE ON spools FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_print_jobs_updated_at BEFORE UPDATE ON print_jobs FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert default admin user (password: admin123 - change in production!)
INSERT INTO users (username, email, password_hash, role) VALUES 
('admin', 'admin@filadb.local', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj6hsxq/3Haa', 'admin');

-- Insert some default materials
INSERT INTO materials (name, density, extruder_temp_min, extruder_temp_max, bed_temp_min, bed_temp_max) VALUES
('PLA', 1.24, 190, 220, 0, 60),
('ABS', 1.04, 220, 260, 80, 110),
('PETG', 1.27, 220, 250, 70, 90),
('TPU', 1.20, 210, 230, 20, 50),
('ASA', 1.07, 240, 260, 90, 110),
('PC', 1.20, 270, 310, 90, 120);

-- Insert some default manufacturers
INSERT INTO manufacturers (name, website) VALUES
('Prusament', 'https://www.prusa3d.com/'),
('Hatchbox', 'https://www.hatchbox3d.com/'),
('eSUN', 'https://www.esun3d.com/'),
('Polymaker', 'https://polymaker.com/'),
('Bambu Lab', 'https://bambulab.com/'),
('Overture', 'https://overture3d.com/');
