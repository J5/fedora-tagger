-- Remove link between Tag and TagLabel
ALTER TABLE tag DROP CONSTRAINT tag_label_id_fkey;

-- Add label entry into Tag

ALTER TABLE tag ADD COLUMN label character varying(255);

UPDATE tag SET label = tag_label.label
FROM tag_label
WHERE tag.label_id = tag_label.id;

-- remove table package_tag_association

DROP TABLE package_tag_association;

-- remove table tag_label
 
DROP TABLE tag_label;

-- Add Rating table

CREATE TABLE rating (
    id SERIAL NOT NULL,
    user_id INTEGER,
    package_id INTEGER,
    rating INTEGER NOT NULL,
    CONSTRAINT rating_id PRIMARY KEY (id),
    CONSTRAINT unique_rating_pkg UNIQUE (package_id, user_id),
    CONSTRAINT user_id_fkey FOREIGN KEY (user_id)
      REFERENCES "user" (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION,
    CONSTRAINT package_id_fkey FOREIGN KEY (package_id)
      REFERENCES package (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION
)
WITH (
  OIDS=FALSE
);


-- Clean the TG tables
DROP TABLE tg_user_group;
DROP TABLE tg_group_permission;
DROP TABLE tg_permission;
DROP TABLE tg_group;
DROP TABLE tg_user;

-- Add the score entry to the user table

ALTER TABLE "user" ADD COLUMN score INTEGER NOT NULL DEFAULT 0;
ALTER TABLE "user" ADD COLUMN api_token VARCHAR(50) DEFAULT NULL;
ALTER TABLE "user" ADD COLUMN api_date DATE DEFAULT CURRENT_DATE;
ALTER TABLE "user" ADD COLUMN anonymous BOOLEAN DEFAULT FALSE;

UPDATE TABLE "user" SET anonymous = TRUE where name = "anonymous";

---- Add Unique Constraints

--ALTER TABLE tag ADD CONSTRAINT unique_package_label UNIQUE (package_id, label);
--ALTER TABLE "package" ADD CONSTRAINT unique_package UNIQUE (name);
--ALTER TABLE vote ADD CONSTRAINT unique_vote_tag UNIQUE (tag_id, user_id);


---- -- Queries to check duplicates:

---- in packages
--SELECT name, cnt FROM (
   --SELECT name, COUNT(name) AS cnt
   --FROM package
   --GROUP BY name
   --ORDER BY cnt DESC ) AS sub
--WHERE cnt > 1;

---- in tag

--SELECT label_id, cnt, cntlabel FROM (
   --SELECT label_id, package_id, COUNT(label_id) AS cntlabel, COUNT(package_id) AS cnt
   --FROM tag
   --GROUP BY label_id, package_id
   --ORDER BY cnt DESC ) AS sub
--WHERE cnt > 1;

---- in vote

--SELECT user_id, tag_id, cnt, cntlabel FROM (
   --SELECT tag_id, user_id, COUNT(user_id) AS cntlabel, COUNT(tag_id) AS cnt
   --FROM vote
   --GROUP BY tag_id, user_id
   --ORDER BY cnt DESC ) AS sub
--WHERE cnt > 1;
