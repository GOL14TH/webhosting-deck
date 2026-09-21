# Power cuts, recovery and backups

The UPS can bridge short outages and provides time for a clean shutdown. Runtime depends on battery capacity and condition, Pi load, display and peripherals.

For unattended recovery, follow the current UPS HAT (D) manufacturer instructions for enabling boot when power returns through its MCU at `0x2d`. Test the full outage-and-return sequence before relying on it.

Keep backups of the static site, non-secret configuration and an encrypted copy of tunnel credentials. Test restoration onto a spare card; an untested backup is only a hope.

## Optional second server

A second Pi can serve the same static site, but DNS alone is not instant failover. Use a health-aware external load balancer or multiple tunnel connectors in a deliberately tested design. Expose only the website from the backup machine, synchronize content intentionally and keep unrelated services private.
