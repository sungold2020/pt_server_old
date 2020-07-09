
CREATE TABLE `download` (
  `Number` smallint NOT NULL DEFAULT '0',
  `Copy` tinyint NOT NULL DEFAULT '0',
  `downloadlink` char(200) DEFAULT '',
  `hash` char(100) DEFAULT '',
  primary key (hash)
) 
