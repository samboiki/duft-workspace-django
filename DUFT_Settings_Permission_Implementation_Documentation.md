# DUFT Settings Permission Implementation Documentation

## Overview

This document outlines the comprehensive implementation of permission-based access control for the DUFT (Data Unified Functional Tools) settings system. The implementation ensures that only authorized users can access and modify system settings while providing a seamless user experience.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Permission System](#permission-system)
3. [Frontend Implementation](#frontend-implementation)
4. [Backend Implementation](#backend-implementation)
5. [Database Configuration](#database-configuration)
6. [Security Considerations](#security-considerations)
7. [User Experience](#user-experience)
8. [Testing Strategy](#testing-strategy)
9. [Deployment Notes](#deployment-notes)

## Architecture Overview

The DUFT settings permission system implements a multi-layered approach:

- **Frontend Permission Gates**: React components check permissions before rendering UI elements
- **Backend Authorization**: Django REST API validates permissions on each request
- **Database Security**: PostgreSQL with proper user access controls
- **Configuration Management**: Settings-driven feature toggles

## Permission System

### Permission Types

#### Core Permissions
- `api.change_settings` - Allows modification of system settings
- `api.view_settings` - Allows viewing of system settings
- `api.run_data_task` - Allows execution of data tasks
- `api.view_dashboard` - Allows access to dashboards

#### Permission Hierarchy
1. **Superuser** - Has all permissions automatically (Django default)
2. **Admin User** - Has `change_settings` permission explicitly assigned
3. **Regular User** - Has limited permissions based on role
4. **Anonymous User** - No access to settings (if authentication enabled)

### Permission Validation Logic

```typescript
const hasAdminRights = (() => {
  // If authentication is disabled, allow access
  if (!config?.features?.user_authentication) {
    return true;
  }

  // If user is not authenticated, deny access
  if (!config?.currentUser) {
    return false;
  }

  // Check if user has change_settings permission
  const hasChangeSettingsPermission =
    config?.currentUserPermissions?.includes("api.change_settings") ?? false;

  // Check if user is a superuser (has all core permissions)
  const hasCorePermissions = [
    "api.change_settings",
    "api.run_data_task", 
    "api.view_dashboard",
  ].every(
    (permission) =>
      config?.currentUserPermissions?.includes(permission) ?? false,
  );

  return hasChangeSettingsPermission || hasCorePermissions;
})();
```

## Frontend Implementation

### Settings Navigation Component

**File**: `/duft-ui/src/features/app-shell/duft-layout-and-navigation/app-layout/side-navigation-bar/settings-and-about-nav-items.tsx`

#### Key Features:
- **Permission Gating**: Only shows settings to authorized users
- **Visual Feedback**: Disabled state for unauthorized access attempts
- **Toast Notifications**: Informative messages for access denied scenarios
- **Dynamic Visibility**: Respects configuration-driven settings

#### Implementation Details:

```tsx
export const SettingsAndAboutNavItems: FC<SettingsAndAboutNavItemsProps> = ({
  setIsSettingsOpen,
  setIsAboutOpen,
}) => {
  const { config } = useAppStore();
  const { data: settings } = useSettings();
  const turnOnAi = config?.features?.ai_engine;

  const showSettings = settings?.["show-settings"] ?? true;
  const showVisualBuilder = settings?.["show-visual-builder"] ?? true;

  // Permission check implementation
  const hasAdminRights = (() => {
    // Authentication bypass logic
    if (!config?.features?.user_authentication) {
      return true;
    }

    // User authentication validation
    if (!config?.currentUser) {
      return false;
    }

    // Permission validation
    const hasChangeSettingsPermission =
      config?.currentUserPermissions?.includes("api.change_settings") ?? false;

    // Superuser detection via core permissions
    const hasCorePermissions = [
      "api.change_settings",
      "api.run_data_task",
      "api.view_dashboard",
    ].every(
      (permission) =>
        config?.currentUserPermissions?.includes(permission) ?? false,
    );

    return hasChangeSettingsPermission || hasCorePermissions;
  })();

  return (
    <Sidebar.ItemGroup key="home-group">
      {showSettings && (
        <SidebarNavLink
          to="#"
          icon={MdOutlineSettings}
          onClick={(e) => {
            e.preventDefault();
            if (hasAdminRights) {
              setIsSettingsOpen(true);
            } else {
              showToast(
                "Access Denied",
                "warning",
                "You need administrator privileges to access Settings. Please contact your system administrator for assistance.",
                5000,
              );
            }
          }}
          className={!hasAdminRights ? "cursor-not-allowed opacity-50" : ""}
        >
          Settings
        </SidebarNavLink>
      )}
      
      {/* Other navigation items */}
    </Sidebar.ItemGroup>
  );
};
```

#### User Experience Features:
- **Graceful Degradation**: Settings option visible but disabled for unauthorized users
- **Clear Messaging**: Toast notifications explain why access is denied
- **Visual Indicators**: Opacity and cursor changes indicate restricted access
- **Helpful Guidance**: Messages direct users to contact administrators

## Backend Implementation

### Django Permission Model

#### Settings API Endpoints
- **GET** `/api/settings/` - Requires `view_settings` permission
- **POST** `/api/settings/` - Requires `change_settings` permission
- **PUT** `/api/settings/{id}/` - Requires `change_settings` permission
- **DELETE** `/api/settings/{id}/` - Requires `change_settings` permission

#### Permission Decorators

```python
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.decorators import permission_required

class SettingsViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, HasSettingsPermission]
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [IsAuthenticated, HasViewSettingsPermission]
        else:
            permission_classes = [IsAuthenticated, HasChangeSettingsPermission]
        return [permission() for permission in permission_classes]
```

#### Custom Permission Classes

```python
from rest_framework import permissions

class HasChangeSettingsPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.has_perm('api.change_settings')

class HasViewSettingsPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.has_perm('api.view_settings')
```

## Database Configuration

### PostgreSQL Setup

The system uses PostgreSQL with the following configuration:

```json
{
  "EPMS_Destination": {
    "type": "PostgreSQL",
    "server": "127.0.0.1",
    "username": "postgres",
    "password": "postgres",
    "port": "5432",
    "database": "qe_data"
  }
}
```

### Docker Compose Configuration

**File**: `docker-compose.yml`

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: duft-postgres
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: qe_data
      POSTGRES_HOST_AUTH_METHOD: trust
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init-scripts:/docker-entrypoint-initdb.d
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres -d qe_data"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s

volumes:
  postgres_data:
    driver: local

networks:
  default:
    name: duft-network
```

### Database Quick Start

```bash
# Start the database
docker-compose up -d postgres

# Connect to the database
docker-compose exec postgres psql -U postgres -d qe_data

# View logs
docker-compose logs postgres

# Stop the database
docker-compose down
```

## Security Considerations

### Authentication Bypass Mode
- **Development Mode**: Authentication can be disabled for development
- **Production Security**: Always enable authentication in production
- **Feature Flags**: Use configuration to control authentication requirements

### Permission Validation
- **Frontend Validation**: UI-level permission checks for user experience
- **Backend Enforcement**: Server-side validation for security
- **Database Level**: Row-level security for sensitive data

### Session Management
- **Token Expiration**: Implement proper session timeout
- **Permission Refresh**: Reload permissions on significant actions
- **Audit Logging**: Track permission-related activities

## User Experience

### Access Scenarios

#### Scenario 1: Authorized Admin User
1. User navigates to settings
2. Permission check passes
3. Settings modal/page opens normally
4. User can modify settings
5. Changes are saved successfully

#### Scenario 2: Unauthorized Regular User
1. User sees settings option (but grayed out)
2. User clicks on settings
3. Toast notification appears: "Access Denied"
4. Helpful message guides user to contact administrator
5. Settings modal/page does not open

#### Scenario 3: Unauthenticated User (if auth enabled)
1. Settings option may be hidden completely
2. If clicked, redirected to login
3. After login, permission check determines access

#### Scenario 4: Development Mode (auth disabled)
1. All users have full access
2. No permission checks performed
3. Settings work normally for all users

### Error Handling
- **Graceful Degradation**: System remains functional even with permission errors
- **Clear Messaging**: Users understand why access is restricted
- **Recovery Paths**: Users know how to gain proper access
- **No Data Loss**: Failed operations don't corrupt existing settings

## Testing Strategy

### Unit Tests
- Permission validation functions
- Component rendering with different permission states
- API endpoint access control

### Integration Tests
- End-to-end permission flows
- Authentication integration
- Database access patterns

### User Acceptance Tests
- Admin user workflow
- Regular user restrictions
- Error message clarity

### Security Tests
- Permission bypass attempts
- Privilege escalation scenarios
- Authentication edge cases

## Deployment Notes

### Environment Configuration
- Set appropriate authentication flags for environment
- Configure proper database credentials
- Enable audit logging in production

### Database Migration
- Run Django migrations for permission tables
- Assign initial permissions to admin users
- Verify permission inheritance

### Monitoring
- Track permission-related errors
- Monitor unauthorized access attempts
- Log settings modification activities

### Performance Considerations
- Cache permission checks where appropriate
- Optimize database queries for permission validation
- Consider permission refresh frequency

## Troubleshooting

### Common Issues
1. **Settings not accessible**: Check user permissions and authentication status
2. **Database connection errors**: Verify PostgreSQL container is running
3. **Permission errors**: Ensure proper Django permissions are assigned
4. **UI not updating**: Check frontend permission state management

### Debugging Steps
1. Verify authentication configuration
2. Check user permissions in Django admin
3. Test database connectivity
4. Review frontend console for permission errors
5. Examine backend logs for authorization failures

## Future Enhancements

### Planned Features
- Role-based permission templates
- Granular settings permissions
- Permission audit trail
- Self-service permission requests
- Dynamic permission assignment

### Scalability Considerations
- Permission caching strategies
- Distributed authentication
- Multi-tenant permission isolation
- Performance optimization for large user bases

---

## Implementation Status

✅ **Completed**:
- Frontend permission gating
- User experience improvements
- Toast notification system
- Visual feedback for restricted access
- Database configuration
- Documentation

🔄 **In Progress**:
- Backend API permission enforcement
- Comprehensive testing suite
- Production deployment scripts

📋 **Planned**:
- Advanced permission management UI
- Audit logging system
- Performance optimization
- Multi-role support

---

*Last Updated: November 19, 2025*
*Version: 1.0.0*
*Authors: DUFT Development Team*
