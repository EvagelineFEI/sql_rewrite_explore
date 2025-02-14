-- case1 original
SELECT * FROM posts 
LEFT JOIN topic_allowed_groups AS tg 
ON posts.topic_id = tg.topic_id 
WHERE tg.id IS NULL AND posts.topic_id 
IN 
(SELECT tau.topic_id FROM topic_allowed_users AS tau 
INNER JOIN topic_allowed_users AS tau2 
ON tau2.topic_id = tau.topic_id AND tau2.id <> tau.id 
WHERE tau.user_id = 1086 AND tau.topic_id = posts.topic_id 
GROUP BY tau.topic_id HAVING COUNT(*) = 1)

-- case1 rewritten by dba
SELECT * FROM posts 
LEFT JOIN topic_allowed_groups tg 
ON posts.topic_id = tg.topic_id 
WHERE tg.id IS NULL AND posts.topic_id 
IN 
(SELECT tau.topic_id FROM topic_allowed_users tau 
JOIN topic_allowed_users tau2 
ON tau2.topic_id = tau.topic_id AND tau2.id != tau.id 
WHERE tau.user_id = 1086 
GROUP BY tau.topic_id HAVING COUNT(*) = 1)

-- case1 rewritten by gpt-o1 version1
SELECT 
    p.*, 
    tg.*
FROM 
    posts AS p
LEFT JOIN 
    topic_allowed_groups AS tg 
    ON p.topic_id = tg.topic_id
WHERE 
    tg.id IS NULL
    AND EXISTS (
        SELECT 1
        FROM topic_allowed_users AS tau
        WHERE tau.user_id = 1086
          AND tau.topic_id = p.topic_id
        GROUP BY tau.topic_id
        HAVING COUNT(tau.id) = 1
    );

-- case1 rewritten by gpt-o1 version2
SELECT 
    p.post_id, 
    p.title, 
    tg.group_id
FROM 
    posts AS p
LEFT JOIN 
    topic_allowed_groups AS tg 
    ON p.topic_id = tg.topic_id
WHERE 
    tg.id IS NULL
    AND EXISTS (
        SELECT 1
        FROM topic_allowed_users AS tau
        WHERE tau.user_id = 1086
          AND tau.topic_id = p.topic_id
        GROUP BY tau.topic_id
        HAVING COUNT(tau.id) = 1
    );

-- case1 rewritten by gpt-o1 with note
SELECT 
    p.*, 
    tg.*
FROM 
    posts AS p
LEFT JOIN 
    topic_allowed_groups AS tg 
    ON p.topic_id = tg.topic_id
WHERE 
    tg.id IS NULL
    AND EXISTS (
        SELECT 1
        FROM topic_allowed_users AS tau
        WHERE tau.user_id = 1086
          AND tau.topic_id = p.topic_id
        GROUP BY tau.topic_id
        HAVING COUNT(tau.id) = 1
    )
    AND NOT EXISTS (
        SELECT 1
        FROM topic_allowed_users AS tau2
        WHERE tau2.topic_id = p.topic_id
          AND tau2.user_id <> 1086
    );

-- case1 rewritten by yvyang
SELECT posts.id, posts.title, posts.content FROM posts 
INNER JOIN topic_allowed_groups AS tg 
ON posts.topic_id = tg.topic_id 
WHERE tg.id IS NULL 
AND EXISTS 
(SELECT 1 FROM topic_allowed_users AS tau 
WHERE tau.topic_id = posts.topic_id AND tau.user_id = 1086 
GROUP BY tau.topic_id HAVING COUNT(*) = 1)