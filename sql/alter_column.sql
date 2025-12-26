-- 如果还没创建 ENUM，则先创建
CREATE TYPE gender_enum AS ENUM ('male','female','other');
CREATE TYPE user_type_enum AS ENUM ('admin','normal');

-- 删除旧列
ALTER TABLE users DROP COLUMN gender;
ALTER TABLE users DROP COLUMN "type";

-- 新建 ENUM 类型的列
ALTER TABLE users ADD COLUMN gender gender_enum;
ALTER TABLE users ADD COLUMN user_type user_type_enum;