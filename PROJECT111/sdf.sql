DROP DATABASE IF EXISTS sideproj;

CREATE DATABASE sideproj;

USE sideproj;

CREATE TABLE Users (
user_id INT PRIMARY KEY AUTO_INCREMENT,  -- 유저 번호
name VARCHAR(50),  -- 이름
birthdate DATE,  --  생년월일
email VARCHAR(100) UNIQUE,  -- 이메일
password_hash VARCHAR(255),  -- 비밀번호(해시)
introduction TEXT,  -- 자기소개
created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE Skills (
skill_id INT PRIMARY KEY AUTO_INCREMENT,  -- 스킬 번호
name VARCHAR(50)  -- 스킬명
);


CREATE TABLE UserSkills (
user_id INT,  -- 유저 번호(FK)
skill_id INT,  -- 스킬 번호(FK)
proficiency_level ENUM('Beginner', 'Intermediate', 'Advanced'),  -- 스택 레벨
FOREIGN KEY (user_id) REFERENCES Users(user_id),
FOREIGN KEY (skill_id) REFERENCES Skills(skill_id),
PRIMARY KEY (user_id, skill_id)  -- 유저 번호와 스킬 번호가 PK
);


CREATE TABLE Projects (
    project_id INT PRIMARY KEY AUTO_INCREMENT,  -- 프로젝트 아이디
    creator_id INT,  -- 진행자 아이디(유저 아이디)
    title VARCHAR(100),  -- 프로젝트 명
    description TEXT,  -- 프로젝트 설명
     goal TEXT,  -- 프로젝트 목표
    tech_stack TEXT,  --  예: 'React, Node.js, Figma' 요구 기술
    is_open BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (creator_id) REFERENCES Users(user_id)
);


CREATE TABLE Teams (
    team_id INT PRIMARY KEY AUTO_INCREMENT,  -- 팀 아이디
    project_id INT,  -- 프로젝트 아이디
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES Projects(project_id)
);


CREATE TABLE TeamMembers (
    team_id INT,  -- 팀 아이디
    user_id INT,  -- 유저 아이디
    role VARCHAR(50),  -- 역할
    joined_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (team_id) REFERENCES Teams(team_id),
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    PRIMARY KEY (team_id, user_id)
);


CREATE TABLE MatchScores (
    match_id INT PRIMARY KEY AUTO_INCREMENT,  -- 매칭 아이디
    user_id INT,  -- 유저 아이디
    project_id INT,  -- 프로젝트 아이디
    score FLOAT,  -- 매칭 점수
    evaluated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (project_id) REFERENCES Projects(project_id)
);


CREATE TABLE Evaluations (
    evaluation_id INT PRIMARY KEY AUTO_INCREMENT,  -- 상호평가 아이디
    evaluator_id INT,  -- 평가자 아이디
    evaluatee_id INT,  -- 평가 당하는 사람 아이디
    team_id INT,  -- 팀 아이디
    score INT CHECK(score BETWEEN 1 AND 5),  -- 평가 점수
    feedback TEXT,  -- 평가 피드백
    evaluated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (evaluator_id) REFERENCES Users(user_id),
    FOREIGN KEY (evaluatee_id) REFERENCES Users(user_id),
    FOREIGN KEY (team_id) REFERENCES Teams(team_id)
);


CREATE TABLE Portfolios (
    portfolio_id INT PRIMARY KEY AUTO_INCREMENT,  -- 포트폴리오 아이디
    user_id INT,  -- 유저 아이디
    project_id INT,  -- 프로젝트 아이디
    description TEXT,  -- 설명
    url VARCHAR(255),  -- 예: Github 링크
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (project_id) REFERENCES Projects(project_id)
);


ALTER TABLE Users
ADD COLUMN available_region VARCHAR(20),
ADD COLUMN github_url VARCHAR(200),
ADD COLUMN portfolio_url VARCHAR(200),
ADD COLUMN major VARCHAR(20),
ADD COLUMN specialty VARCHAR(255),
ADD COLUMN tech_stack VARCHAR(255),
ADD COLUMN collaboration_tools VARCHAR(255),
ADD COLUMN experience_level VARCHAR(10),
ADD COLUMN collaboration_style VARCHAR(10),
ADD COLUMN meeting_frequency VARCHAR(20),
ADD COLUMN belbin_role VARCHAR(3),
ADD COLUMN preferred_team_size VARCHAR(10),
ADD COLUMN preferred_project_topics VARCHAR(255),
ADD COLUMN availability_period VARCHAR(10),
ADD COLUMN is_profile_complete BOOLEAN NOT NULL DEFAULT FALSE;

ALTER TABLE Users ADD COLUMN last_login DATETIME NULL;
ALTER TABLE Users ADD COLUMN is_staff BOOLEAN;
ALTER TABLE Users ADD COLUMN is_active BOOLEAN;
ALTER TABLE Users ADD COLUMN is_superuser BOOLEAN;

SELECT * FROM `ProjectEmbeddings` LIMIT 100;