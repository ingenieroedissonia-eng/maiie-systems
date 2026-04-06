content = open('maiie-web/src/components/MissionForm.jsx', 'r', encoding='utf-8').read()

old = '''handleSubmit = (event) => {
        event.preventDefault();
        setError('');

        if (!missionName.trim() || !missionDescription.trim()) {
            setError('Both mission name and description are required.');
            return;
        }

        setIsSubmitting(true);

        try {
            onSendOrder({
                name: missionName,
                description: missionDescription,
            });'''

new = '''handleSubmit = async (event) => {
        event.preventDefault();
        if (isSubmitting) return;
        setError('');

        if (!missionName.trim() || !missionDescription.trim()) {
            setError('Both mission name and description are required.');
            return;
        }

        setIsSubmitting(true);

        try {
            await onSendOrder({
                name: missionName,
                description: missionDescription,
            });'''

if old in content:
    open('maiie-web/src/components/MissionForm.jsx', 'w', encoding='utf-8').write(content.replace(old, new))
    print("FIX APLICADO")
else:
    print("NO MATCH")
