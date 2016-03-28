DROP TABLE IF EXISTS utilizadores;
DROP TABLE IF EXISTS artigos;
DROP TABLE IF EXISTS palavraschave;
DROP TABLE IF EXISTS imagens;
DROP TABLE IF EXISTS licitacoes;
DROP TABLE IF EXISTS perguntas;


CREATE TABLE utilizadores(
	user_id   INT 		PRIMARY KEY AUTO_INCREMENT,
	admin   tinyint(1) DEFAULT 0,
	nick		CHAR(12)	UNIQUE,
	nome		VARCHAR(32) NOT NULL,
	apelido		VARCHAR(32) NOT NULL,
	email		VARCHAR(32)	UNIQUE,
	pais		VARCHAR(32) NOT NULL,
	concelho	VARCHAR(32),
	distrito	VARCHAR(32),
	foto		VARCHAR(64),
	data_reg	DATETIME
) ENGINE=INNODB;

CREATE TABLE artigos(
	item_id		INT	PRIMARY KEY AUTO_INCREMENT,
	designacao	VARCHAR(64) NOT NULL,
	user_id		INT REFERENCES utilizadores(user_id),
	valor_base	NUMERIC(10,2) NOT NULL,
	descricao	TEXT,
	data_entr	DATETIME,
	data_fim	DATETIME,
	melhor_lic	INT REFERENCES utilizadores(user_id),
	melhor_val	NUMERIC(10,2)
)  ENGINE=INNODB;

CREATE TABLE palavraschave(
	item_id		INT REFERENCES artigos(item_id),
	pal_chave	VARCHAR(16),
	CONSTRAINT	pk_keyword PRIMARY KEY(item_id, pal_chave)
) ENGINE=INNODB;

CREATE TABLE imagens(
	item_id		INT REFERENCES artigos(item_id),
	nome_img	VARCHAR(64),
	CONSTRAINT	pk_images PRIMARY KEY(item_id, nome_img)
) ENGINE=INNODB;

CREATE TABLE licitacoes(
	user_id		INT REFERENCES utilizadores(user_id) ON DELETE CASCADE,
	item_id 	INT REFERENCES artigos(item_id)  ON DELETE CASCADE,
	data_licit	DATETIME,
	valor		NUMERIC(10,2),
	CONSTRAINT pk_bids PRIMARY KEY (user_id, item_id, data_licit)
) ENGINE=INNODB;

CREATE TABLE tags(
	tag_id		INT,
	user_id		INT REFERENCES utilizadores(user_id) ON DELETE CASCADE,
	item_id 	INT REFERENCES artigos(item_id)  ON DELETE CASCADE,
	CONSTRAINT pk_tags PRIMARY KEY (tag_id)
) ENGINE=INNODB;

CREATE TABLE perguntas(
	user_id		INT REFERENCES utilizadores(user_id) ON DELETE CASCADE,
	item_id 	INT REFERENCES artigos(item_id)  ON DELETE CASCADE,
	data_perg	DATETIME NOT NULL,
	data_resp	DATETIME NOT NULL,
	pergunta	VARCHAR(256) NOT NULL,
	resposta	VARCHAR(256),
	CONSTRAINT pk_questions PRIMARY KEY (user_id, item_id, data_perg)
) ENGINE=INNODB;

