"""
多库路由：按 app_label 分库
auth_app/system_app -> default (campus_system)
academic_app -> academic
resource_app -> resource
finance_app -> finance
health 相关可走 health
"""
APP_DB_MAP = {
    'auth_app': 'default',
    'system_app': 'default',
    'academic_app': 'academic',
    'resource_app': 'resource',
    'finance_app': 'finance',
}

class CampusRouter:
    def db_for_read(self, model, **hints):
        return APP_DB_MAP.get(model._meta.app_label)

    def db_for_write(self, model, **hints):
        return APP_DB_MAP.get(model._meta.app_label)

    def allow_relation(self, obj1, obj2, **hints):
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        target = APP_DB_MAP.get(app_label)
        if target is None:
            return db == 'default'
        return db == target
