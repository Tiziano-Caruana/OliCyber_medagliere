python3 main.py

# esegui tutti i file_builders
for f in $(find ../file_builders -name "*.py"); do
    python3 $f
done