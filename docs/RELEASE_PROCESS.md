# Release Process

## Semantic Versioning

Format: `MAJOR.MINOR.PATCH`

- **MAJOR** (0→1): Breaking API changes
- **MINOR** (0→1): New features (backward-compatible)
- **PATCH** (0→1): Bug fixes

Current version: **0.1.0**

## Release Checklist

1. **Update version**
   ```bash
   # Edit pyproject.toml, Dockerfile, helm/Chart.yaml
   # Change version: 0.1.0 → 0.1.1 (or 0.2.0, etc)
   git add -A
   git commit -m "chore: bump version to 0.1.1"
   ```

2. **Update CHANGELOG.md**
   ```markdown
   ## [0.1.1] - 2026-06-23
   
   ### Fixed
   - Fixed latency issue in audit log queries
   
   ### Added
   - New performance baseline documentation
   ```

3. **Test thoroughly**
   ```bash
   make test          # All unit tests
   make load-test     # Performance regression
   make coverage      # Verify 80%+ coverage
   ```

4. **Create release tag**
   ```bash
   git tag -a v0.1.1 -m "Release version 0.1.1"
   git push origin v0.1.1
   ```

5. **GitHub release**
   ```bash
   gh release create v0.1.1 --generate-notes
   ```

6. **Build & push Docker image**
   ```bash
   docker build -t aerosense:0.1.1 .
   docker tag aerosense:0.1.1 aerosense:latest
   docker push aerosense:0.1.1
   docker push aerosense:latest
   ```

7. **Deploy to production**
   ```bash
   helm upgrade aerosense ./helm \
     --set image.tag=0.1.1 \
     -n aerosense
   ```

8. **Verify deployment**
   ```bash
   kubectl rollout status deployment/aerosense-app -n aerosense
   ```

## Communication

- Announce in #engineering Slack
- Tag in GitHub Release notes
- Update status page if applicable

## Rollback

If release breaks production:
```bash
# Rollback to previous version
helm rollback aerosense -n aerosense

# Or deploy previous tag
helm upgrade aerosense ./helm \
  --set image.tag=0.1.0 \
  -n aerosense
```

## Schedule

- **Patch releases:** As needed (bug fixes)
- **Minor releases:** Monthly (new features)
- **Major releases:** Planned (breaking changes)
