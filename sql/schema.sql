USE master;
GO

IF DB_ID('Tennis') IS NOT NULL
BEGIN
    ALTER DATABASE Tennis SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE Tennis;
END
GO

CREATE DATABASE Tennis;
GO

USE Tennis;
GO

CREATE TABLE Tournament (
    tourney_id     VARCHAR(50)  NOT NULL,
    tourney_name   VARCHAR(100) NOT NULL,
    tourney_date   DATE         NOT NULL,
    tourney_level  VARCHAR(5)   NOT NULL,
    surface        VARCHAR(10)  NULL,
    CONSTRAINT PK_Tournament PRIMARY KEY (tourney_id)
);

CREATE TABLE Player (
    player_id   INT          NOT NULL,
    name_first  VARCHAR(50)  NULL,
    name_last   VARCHAR(50)  NOT NULL,
    hand        CHAR(1)      NULL,
    dob         DATE         NULL,
    ioc         CHAR(3)      NULL,
    height      SMALLINT     NULL,
    CONSTRAINT PK_Player PRIMARY KEY (player_id)
);

CREATE TABLE TennisMatch (
    match_id       INT IDENTITY(1,1) NOT NULL,
    tourney_id     VARCHAR(50)  NOT NULL,
    match_num      INT          NOT NULL,
    round          VARCHAR(10)  NOT NULL,
    winner_id      INT          NOT NULL,
    loser_id       INT          NOT NULL,
    winner_rank    INT          NULL,
    loser_rank     INT          NULL,
    score          VARCHAR(50)  NULL,
    is_wo          BIT          NOT NULL CONSTRAINT DF_TennisMatch_IsWo DEFAULT 0,
    is_retirement  BIT          NOT NULL CONSTRAINT DF_TennisMatch_IsRetirement DEFAULT 0,
    CONSTRAINT PK_TennisMatch PRIMARY KEY (match_id),
    CONSTRAINT UQ_TennisMatch_TourneyMatch UNIQUE (tourney_id, match_num),
    CONSTRAINT FK_TennisMatch_Tournament FOREIGN KEY (tourney_id) REFERENCES Tournament (tourney_id),
    CONSTRAINT FK_TennisMatch_Winner FOREIGN KEY (winner_id) REFERENCES Player (player_id),
    CONSTRAINT FK_TennisMatch_Loser FOREIGN KEY (loser_id) REFERENCES Player (player_id)
);