# TODO

- [x] Fix incorrect imports and wiring in `server/app/api/auth_api.py` (use `app.modules.profile.auth_service.AuthService`).
- [x] Fix/add `profile` router inclusion in `server/app/main.py`.
- [x] Ensure `server/app/api/profile_api.py` imports are correct and endpoints work.
- [x] Implement missing/empty routes in `server/app/modules/profile/profile_api.py` or ensure it’s not used.
- [x] Ensure repository is created/linked only via project creation; prevent direct public repository API.

- [x] Run a quick import/start check for the FastAPI app.
- [x] Wire auth/profile routers (and remove public repository router)


