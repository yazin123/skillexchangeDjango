# core/migrations/0002_initial_skills.py
from django.db import migrations

def create_initial_skills(apps, schema_editor):
    Skill = apps.get_model('core', 'Skill')
    initial_skills = [
        {'name': 'Python Programming', 'category': 'Programming', 'description': 'Python programming language'},
        {'name': 'Web Development', 'category': 'Programming', 'description': 'Web development with HTML, CSS, and JavaScript'},
        {'name': 'Digital Marketing', 'category': 'Marketing', 'description': 'Digital marketing and social media'},
        {'name': 'Graphic Design', 'category': 'Design', 'description': 'Graphic design with modern tools'},
        {'name': 'English Language', 'category': 'Language', 'description': 'English language teaching and learning'},
    ]
    
    for skill_data in initial_skills:
        Skill.objects.create(**skill_data)

class Migration(migrations.Migration):
    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_initial_skills),
    ]