# Nyāya Corpus - GitHub Repository Setup Commands
# Run these commands to create and upload the repository to GitHub

# Step 1: Create a new repository on GitHub
# Go to https://github.com/new and create a repository named "nyaya-corpus"
# Set it as Public repository
# DO NOT initialize with README, .gitignore, or license (we already have these)

# Step 2: Add GitHub remote origin (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/nyaya-corpus.git

# Step 3: Verify remote is set correctly
git remote -v

# Step 4: Push to GitHub
git branch -M main
git push -u origin main

# Step 5: (Optional) Create and push additional branches for development
git checkout -b development
git push -u origin development
git checkout main

# Step 6: (Optional) Create release tag
git tag -a v1.0.0 -m "Nyāya Corpus v1.0.0 - Initial release with 339 validated syllogisms"
git push origin v1.0.0

# Alternative: If you prefer SSH authentication (requires SSH key setup)
# git remote add origin git@github.com:YOUR_USERNAME/nyaya-corpus.git

# Repository Statistics:
# - Total entries: 339 Nyāya syllogisms
# - Cultural distribution: 73% Non-Western, 27% Western
# - Domains: Philosophy (45%), Logic (32%), Sanskrit Grammar (12%)
# - Quality: 100% validation through staging pipeline

echo "Repository setup complete! Your Nyāya Corpus is now on GitHub."
echo "Repository URL: https://github.com/YOUR_USERNAME/nyaya-corpus"
echo "Don't forget to replace YOUR_USERNAME with your actual GitHub username!"
