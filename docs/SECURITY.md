# Security Policy

This document outlines the security policy for PowerGym Backend, including how to report vulnerabilities, security best practices, and security considerations.

## Table of Contents

- [Supported Versions](#supported-versions)
- [Reporting a Vulnerability](#reporting-a-vulnerability)
- [Security Best Practices](#security-best-practices)
- [Authentication & Authorization](#authentication--authorization)
- [Data Protection](#data-protection)
- [Network Security](#network-security)
- [API Security](#api-security)
- [Dependencies](#dependencies)
- [Security Checklist](#security-checklist)

## Supported Versions

Security updates are provided for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

### How to Report

If you discover a security vulnerability, please **do not** open a public issue. Instead, report it privately:

1. **Email**: Send details to the security team (provide contact email)
2. **GitHub Security Advisory**: Use GitHub's private vulnerability reporting (if enabled)
3. **Direct Contact**: Contact the maintainers directly

### What to Include

When reporting a vulnerability, please include:

- **Description**: Clear description of the vulnerability
- **Impact**: Potential impact and severity
- **Steps to Reproduce**: Detailed steps to reproduce the issue
- **Proof of Concept**: If possible, provide a proof of concept
- **Suggested Fix**: If you have a suggested fix
- **Affected Versions**: Which versions are affected

### Response Timeline

- **Initial Response**: Within 48 hours
- **Status Update**: Within 7 days
- **Fix Timeline**: Depends on severity (see below)

### Severity Levels

- **Critical**: Remote code execution, authentication bypass
  - Response: Immediate
  - Fix: Within 7 days
  
- **High**: Data exposure, privilege escalation
  - Response: Within 24 hours
  - Fix: Within 14 days
  
- **Medium**: Information disclosure, denial of service
  - Response: Within 48 hours
  - Fix: Within 30 days
  
- **Low**: Best practice violations, minor issues
  - Response: Within 7 days
  - Fix: Next release

### Disclosure Policy

- Vulnerabilities are disclosed after a fix is available
- Credit will be given to reporters (if desired)
- A security advisory will be published for significant issues

## Security Best Practices

### 1. Environment Variables

**Never commit secrets to version control.**

```bash
# ✅ Good: Use .env file (in .gitignore)
SECRET_KEY=your-secret-key-here

# ❌ Bad: Hardcoded in code
SECRET_KEY = "hardcoded-secret"
```

**Best Practices**:
- Use strong, random secrets (32+ characters)
- Rotate secrets regularly
- Use different secrets for each environment
- Use secret management services in production (AWS Secrets Manager, HashiCorp Vault, etc.)

### 2. Password Security

**Password Hashing**:
- Uses **Argon2** algorithm (industry standard)
- Passwords are never stored in plain text
- Password verification is constant-time

**Password Requirements**:
- Minimum length: 8 characters (enforced by frontend)
- Strong passwords recommended
- Password reset functionality available

### 3. JWT Token Security

**Token Configuration**:
- **Access Tokens**: Short-lived (5 hours default)
- **Refresh Tokens**: Longer-lived (12 hours default)
- **Algorithm**: HS256 (HMAC-SHA256)
- **Secret Key**: Strong, random, never exposed

**Best Practices**:
- Store tokens securely (httpOnly cookies recommended for web)
- Never log tokens
- Implement token rotation
- Revoke tokens on logout
- Use HTTPS in production

### 4. Database Security

**Connection Security**:
- Use strong passwords (16+ characters)
- Restrict database access to application server only
- Use SSL/TLS for database connections in production
- Never expose database port publicly

**Data Protection**:
- Encrypt sensitive data at rest
- Use parameterized queries (SQLAlchemy ORM prevents SQL injection)
- Regular backups with encryption
- Access control and audit logging

### 5. API Security

**Rate Limiting**:
- Enabled by default (60 requests/minute)
- Prevents brute force attacks
- Configurable per environment

**Input Validation**:
- All inputs validated using Pydantic schemas
- Type checking and format validation
- Sanitization of user inputs

**CORS Configuration**:
- Restricted to trusted origins only
- Never use `*` in production
- Configure per environment

## Authentication & Authorization

### Authentication

**JWT-Based Authentication**:
- Stateless authentication
- Token-based (no sessions)
- Refresh token mechanism

**Authentication Flow**:
1. User provides credentials
2. Server validates credentials
3. Server issues access and refresh tokens
4. Client includes access token in requests
5. Server validates token on each request

### Authorization

**Role-Based Access Control (RBAC)**:
- **Admin**: Full access to all resources
- **Employee**: Limited access based on permissions

**Permission Checks**:
- Endpoint-level authorization
- Resource-level authorization
- Automatic permission validation

### Token Management

**Access Token**:
- Short expiration (5 hours)
- Used for API requests
- Stored securely on client

**Refresh Token**:
- Longer expiration (12 hours)
- Used to obtain new access tokens
- Rotated on use (if implemented)

**Token Revocation**:
- Logout invalidates tokens
- Token blacklist (if implemented)
- Expired tokens automatically rejected

## Data Protection

### Encryption

**Biometric Data**:
- Face embeddings: Stored as vectors (not encrypted, needed for search)
- Thumbnails: Encrypted using `BIOMETRIC_ENCRYPTION_KEY`
- Encryption algorithm: AES (via cryptography library)

**Sensitive Data**:
- Passwords: Hashed with Argon2
- API tokens: Stored securely
- Database credentials: In environment variables

### Data Privacy

**Personal Information**:
- DNI numbers: Stored securely
- Contact information: Protected
- Payment information: Not stored (handled externally if needed)

**Compliance**:
- Follow data protection regulations (GDPR, etc.)
- Implement data retention policies
- Provide data export/deletion capabilities

### Backup Security

**Backup Encryption**:
- Encrypt backups before storage
- Secure backup storage location
- Restrict backup access

**Backup Retention**:
- Follow retention policy
- Secure deletion of old backups
- Regular backup verification

## Network Security

### HTTPS/TLS

**Production Requirements**:
- Always use HTTPS in production
- Valid SSL/TLS certificates
- Strong cipher suites
- TLS 1.2+ only

**Certificate Management**:
- Use Let's Encrypt or trusted CA
- Auto-renewal configured
- Monitor certificate expiration

### Firewall Configuration

**Recommended Rules**:
- Block all ports by default
- Allow only necessary ports:
  - 80 (HTTP) - redirect to HTTPS
  - 443 (HTTPS) - API access
  - 22 (SSH) - server management (restrict by IP)
- Block database port (5432) from public

**Example (UFW)**:
```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### Network Isolation

**Docker Networks**:
- Use isolated Docker networks
- Services communicate via internal network
- Database not exposed to host (unless needed)

**Production**:
- Use private networks
- VPN for administrative access
- Network segmentation

## API Security

### Rate Limiting

**Configuration**:
- Default: 60 requests/minute per IP
- Configurable via `RATE_LIMIT_PER_MINUTE`
- Applied to all endpoints

**Implementation**:
- Uses `slowapi` library
- IP-based limiting
- Headers: `X-RateLimit-*`

### Input Validation

**Pydantic Schemas**:
- All requests validated
- Type checking
- Format validation
- Custom validators

**SQL Injection Prevention**:
- SQLAlchemy ORM (parameterized queries)
- No raw SQL with user input
- Input sanitization

### Error Handling

**Security Considerations**:
- Don't expose internal errors
- Generic error messages for users
- Detailed errors in logs only
- No stack traces in production

### CORS Configuration

**Production Settings**:
```env
ALLOWED_ORIGINS_STR=https://app.your-domain.com,https://www.your-domain.com
```

**Development Settings**:
```env
ALLOWED_ORIGINS_STR=http://localhost:5173,http://localhost:3000
```

**Never Use**:
```env
ALLOWED_ORIGINS_STR=*  # ❌ Never in production
```

## Dependencies

### Dependency Management

**Regular Updates**:
- Keep dependencies up to date
- Monitor security advisories
- Use `uv` or `pip` with lock files

**Vulnerability Scanning**:
- Use tools like `safety` or `pip-audit`
- Check for known vulnerabilities
- Update vulnerable dependencies promptly

**Dependency Review**:
```bash
# Check for vulnerabilities
pip-audit

# Or using safety
safety check
```

### Trusted Sources

**Package Sources**:
- Use official PyPI only
- Verify package signatures
- Review package maintainers

**Docker Images**:
- Use official images
- Pin specific versions
- Scan images for vulnerabilities

## Security Checklist

### Development

- [ ] No secrets in code
- [ ] All inputs validated
- [ ] Error handling implemented
- [ ] Logging configured (no sensitive data)
- [ ] Tests include security scenarios

### Pre-Deployment

- [ ] All secrets configured
- [ ] Strong passwords set
- [ ] HTTPS configured
- [ ] CORS restricted
- [ ] Rate limiting enabled
- [ ] Database access restricted
- [ ] Firewall configured
- [ ] Backups configured
- [ ] Monitoring enabled

### Production

- [ ] `DEBUG=false`
- [ ] Strong `SECRET_KEY`
- [ ] Strong `BIOMETRIC_ENCRYPTION_KEY`
- [ ] Database credentials secure
- [ ] HTTPS enforced
- [ ] CORS restricted to production URLs
- [ ] Rate limiting configured
- [ ] Log rotation configured
- [ ] Regular security updates
- [ ] Backup strategy in place

### Ongoing

- [ ] Regular dependency updates
- [ ] Security monitoring
- [ ] Log review
- [ ] Access audit
- [ ] Backup verification
- [ ] Certificate renewal
- [ ] Security patches applied

## Common Security Issues

### 1. Exposed Secrets

**Problem**: Secrets committed to repository

**Solution**:
- Remove from Git history
- Rotate all exposed secrets
- Add to `.gitignore`
- Use secret scanning tools

### 2. Weak Passwords

**Problem**: Default or weak passwords

**Solution**:
- Enforce strong passwords
- Change default admin password
- Use password managers
- Implement password policies

### 3. Missing HTTPS

**Problem**: API accessible via HTTP

**Solution**:
- Configure SSL/TLS certificates
- Redirect HTTP to HTTPS
- Use reverse proxy (Nginx/Traefik)

### 4. Open CORS

**Problem**: CORS allows all origins

**Solution**:
- Restrict to specific origins
- Never use `*` in production
- Validate origin headers

### 5. SQL Injection

**Problem**: Raw SQL with user input

**Solution**:
- Use SQLAlchemy ORM
- Parameterized queries
- Input validation
- No user input in raw SQL

## Security Monitoring

### Logging

**Security Events**:
- Failed login attempts
- Authentication failures
- Authorization denials
- Rate limit violations
- Suspicious activity

**Log Security**:
- Don't log sensitive data
- Encrypt log files
- Restrict log access
- Regular log review

### Monitoring

**Key Metrics**:
- Authentication success/failure rates
- API error rates
- Rate limit hits
- Unusual traffic patterns
- Resource usage

**Alerting**:
- Failed authentication spikes
- High error rates
- Resource exhaustion
- Unusual access patterns

## Incident Response

### If a Vulnerability is Discovered

1. **Assess Impact**: Determine severity and scope
2. **Contain**: Limit exposure if possible
3. **Fix**: Develop and test fix
4. **Deploy**: Deploy fix to production
5. **Notify**: Inform affected users if necessary
6. **Document**: Update security documentation

### If a Breach Occurs

1. **Contain**: Isolate affected systems
2. **Assess**: Determine scope of breach
3. **Notify**: Inform stakeholders
4. **Remediate**: Fix vulnerabilities
5. **Monitor**: Enhanced monitoring
6. **Review**: Post-incident review

## Security Resources

### Tools

- **Dependency Scanning**: `pip-audit`, `safety`
- **Secret Scanning**: `git-secrets`, `truffleHog`
- **Vulnerability Databases**: CVE, GitHub Security Advisories
- **SSL Testing**: SSL Labs, Qualys SSL Test

### References

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [Python Security](https://python.readthedocs.io/en/latest/library/security.html)
- [PostgreSQL Security](https://www.postgresql.org/docs/current/security.html)

## Contact

For security concerns:

- **Email**: [security@powergym.com] (replace with actual email)
- **GitHub Security**: Use private vulnerability reporting
- **Response Time**: Within 48 hours

---

**Last Updated**: 2025-01-15  
**Version**: 1.0

---

**Related Documentation**:
- [Configuration Guide](CONFIGURATION.md) - Security configuration
- [Deployment Guide](DEPLOYMENT.md) - Production security
- [API Documentation](API.md) - API security features

