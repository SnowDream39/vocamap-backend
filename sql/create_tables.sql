create extension postgis;

CREATE TYPE tag_type_enum AS ENUM ('category', 'artist');
CREATE TYPE gender_enum AS ENUM ('male','female','other');

CREATE TABLE tags (
    id SERIAL PRIMARY KEY,
    type tag_type_enum NOT NULL,
    name VARCHAR(100) NOT NULL
);

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(320) NOT NULL UNIQUE,
    hashed_password VARCHAR NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_superuser BOOLEAN NOT NULL DEFAULT FALSE,
    is_verified BOOLEAN NOT NULL DEFAULT FALSE,
    nickname VARCHAR(100) NOT NULL DEFAULT '新用户',
    gender gender_enum NOT NULL DEFAULT 'other',
    age INT,
    signup_time TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE user_tags (
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    tag_id INT REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, tag_id)
);

CREATE INDEX idx_user_tags_user ON user_tags(user_id);
CREATE INDEX idx_user_tags_tag ON user_tags(tag_id);

CREATE TABLE activities (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    start_time TIMESTAMPTZ NOT NULL,
    end_time TIMESTAMPTZ NOT NULL,
	location VARCHAR(200),
    description TEXT,
    max_member INT,
    owner_id INT REFERENCES users(id),
	position geography(Point, 4326)
);

CREATE INDEX idx_activities_position_gist ON activities USING gist(position);
CREATE INDEX idx_activitids_owner ON activities (owner_id);

CREATE TABLE activity_participants (
    activity_id INT REFERENCES activities(id) ON DELETE CASCADE,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    PRIMARY KEY (activity_id, user_id)
);

CREATE INDEX idx_activity_participants_activity ON activity_participants(activity_id);
CREATE INDEX idx_activity_participants_user ON activity_participants(user_id);

CREATE TABLE activity_tags (
    activity_id INT REFERENCES activities(id) ON DELETE CASCADE,
    tag_id INT REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (activity_id, tag_id)
);

CREATE INDEX idx_activity_tags_activity ON activity_tags(activity_id);
CREATE INDEX idx_activity_tags_tag ON activity_tags(tag_id);

INSERT INTO users(email, hashed_password, is_superuser, nickname, gender)
VALUES 
	('759723417@qq.com', 
	'$argon2id$v=19$m=65536,t=3,p=4$+3bysvs0+RpJfLjQdxzrrA$f61IOu5P2n4YA5dmZO64E49XWxlXmFW9KkbWJZ5bm7E', 
	TRUE, 'SnowDream39', 'male');


INSERT INTO tags(type, name)
VALUES
	('artist', 'VOCALOID'),
	('artist', '初音未来'),
	('category', 'KTV'),
	('category', '演唱会'),
    ('category', '同人展');

INSERT INTO activities(name, start_time, end_time, location, description, max_member, position)
VALUES
	('CP32Pre', '2025-12-27:09:00:00+08'::TIMESTAMPTZ, '2025-12-28:18:00:00+08'::TIMESTAMPTZ, 
	'杭州大会展中心', '禁止日本IP，允许中文术力口', 100000, ST_GeogFromText('SRID=4326;POINT(120.42 30.27)')),
	('CP32Pre', '2025-12-27:09:00:00+08'::TIMESTAMPTZ, '2025-12-28:18:00:00+08'::TIMESTAMPTZ, 
	'杭州大会展中心', '禁止日本IP，允许中文术力口', 100000, ST_GeogFromText('SRID=4326;POINT(120.42 30.27)'));

INSERT INTO activity_tags(activity_id, tag_id)
VALUES
	(1, 1),
	(1, 2),
    (1, 5);

