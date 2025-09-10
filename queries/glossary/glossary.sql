--- a/file:///c%3A/Users/fm274/erp-project/Teammate%205/queries/glossary/glossary.sql
--- This query retrieves all glossary terms with their definitions and associated modules.
SELECT 
    glossary_id AS id,
    term,
    definitions,
    module
FROM glossary
where glossary_id = 1;
