-- MySQL dump 10.13  Distrib 8.0.31, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: snow_plume
-- ------------------------------------------------------
-- Server version	8.0.31

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Dumping routines for database 'snow_plume'
--
/*!50003 DROP PROCEDURE IF EXISTS `ero` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `ero`(
user_id CHAR(12),
group_id CHAR(12),
OUT times_of_ero TINYINT UNSIGNED
)
BEGIN	
    -- 检查是否是当天首次
    SET times_of_ero = (SELECT count(*) FROM 
			(SELECT DATE_FORMAT(datetime,'%Y-%m-%d') AS date1 FROM ero AS e WHERE e.user_id=user_id AND e.group_id=group_id) as subquery
            WHERE subquery.date1 = date(now()));
    
    -- 插入数据
	INSERT INTO ero()
    VALUES(
    user_id,
    group_id,
    now()
    );

END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `fortune_get` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `fortune_get`(
	user_id CHAR(12),
    OUT fortune SMALLINT,
	OUT level_name CHAR(2),
    OUT greetings VARCHAR(45),
    OUT greeting_content VARCHAR(45),
    OUT charm_item VARCHAR(20),
    OUT charm_content VARCHAR(45)
)
BEGIN
	DECLARE fortune_value_var,k,level_var,greetings_var,charm_var,a SMALLINT;
    -- 初始化fortune_value
    SET fortune_value_var = floor(rand()*114-3);
    -- 找到fortune_value对应的时运等级，返回level_var（即level_id）
    SET k = 0;
    REPEAT
        SET k = k + 1;
	UNTIL 
		fortune_value_var >= (
			 SELECT value_min FROM fortune_levels
			 WHERE level_id = k-1) 
		AND
        fortune_value_var <= (
			 SELECT value_max FROM fortune_levels
			 WHERE level_id = k-1) 
	END REPEAT;
    SET level_var = (SELECT level_id FROM fortune_levels WHERE level_id = k-1);
	
    -- 根据level_var，抽取对应level的greetings和幸运物
    SET a = floor(rand()*(SELECT COUNT(greetings_fortune_id) FROM fortune_greetings WHERE level_id = level_var));
    SET greetings_var = 
		(SELECT greetings_fortune_id FROM fortune_greetings WHERE level_id = level_var LIMIT 
			a,1);
    
    SET charm_var = floor(rand()*(SELECT COUNT(luck_charm_id) FROM fortune_charms)+1);
    
    -- 将抽签结果写入数据库
	INSERT INTO fortune_get(
			date,
            user_id,
            fortune_value,
            level_id,
            greetings_fortune_id,
            luck_charm_id)
	VALUES(
		DATE(now()),
        user_id,
        fortune_value_var,
        level_var,
        greetings_var,
        charm_var
		);
        
	-- 准备输出
    SET fortune = fortune_value_var,
	    level_name = (SELECT name From fortune_levels WHERE level_id = level_var),
        greetings = (SELECT f.greeting_content FROM fortune_levels AS f WHERE level_id = level_var),
        greeting_content = (SELECT content FROM fortune_greetings WHERE greetings_fortune_id = greetings_var),
        charm_item = (SELECT item From fortune_charms WHERE luck_charm_id = charm_var),
        charm_content = (SELECT content From fortune_charms WHERE luck_charm_id = charm_var);
    
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `fortune_get_when_duplicated` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `fortune_get_when_duplicated`(
	user_id CHAR(12),
    OUT fortune SMALLINT,
	OUT level_name CHAR(2),
    OUT greetings VARCHAR(45),
    OUT greeting_content VARCHAR(45),
    OUT charm_item VARCHAR(20),
    OUT charm_content VARCHAR(45)
	)
BEGIN
	-- 同一user_id在某一天多次请求今日运势时，直接返回已有值
	DECLARE today DATE;
    SET today = DATE(now());
    SET fortune = (
			SELECT fortune_value 
            FROM fortune_get AS g 
            WHERE g.date = today AND g.user_id = user_id),
	    level_name = (
			SELECT name 
			From fortune_levels
			JOIN fortune_get AS g 
			USING (level_id)
			WHERE g.date = today AND g.user_id = user_id),
        greetings = (
			SELECT f.greeting_content 
            FROM fortune_levels AS f
            JOIN fortune_get AS g
            USING (level_id)
            WHERE g.date = today AND g.user_id = user_id),
        greeting_content = (
			SELECT content 
            FROM fortune_greetings 
            JOIN fortune_get AS g
            USING (greetings_fortune_id)
            WHERE g.date = today AND g.user_id = user_id),
        charm_item = (
			SELECT item 
            From fortune_charms
            JOIN fortune_get AS g
            USING (luck_charm_id)
            WHERE g.date = today AND g.user_id = user_id),
        charm_content = (
			SELECT content 
            From fortune_charms
            JOIN fortune_get AS g
            USING (luck_charm_id)
            WHERE g.date = today AND g.user_id = user_id);

END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2022-12-11 21:57:17
