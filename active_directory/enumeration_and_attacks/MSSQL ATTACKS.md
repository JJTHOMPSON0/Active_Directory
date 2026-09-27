# Sysadmin 
check if u are a sysadmin, if are then jsut use xpcmdshell too execute commands .
Default sysadmin of a Mssql server is `sa`

Sysadmin on SQL Server lets you enable `xp_cmdshell`, which runs OS commands as whatever account the _SQL Server service itself_ runs as.
# Impersonation

Check if the the current login user can impersonate another user.
# Session
check if there are any other users which are currently logged in the server.

# Linked Server

A `"linked server"` in MSSQL lets one SQL Server instance transparently run queries against another, using pre-configured credentials.

check if there are nay linked servers, i fthere are , u can communicate with them, and identify if the current user has any interesting rights over that server?

# NTLM relay(IDK)
for stealing TGT of the MSSQL SPN Service by which we can get a domain authenticated user which can easily be possible by any low priv user in the mssql server.

