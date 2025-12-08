import re

# Regex patterns for each prompt level, developed from provided TIO examples
# Patterns are generic: Capture any hostname/model in parentheses, followed by mode-specific suffix
# Anchored with ^ and $ for exact match; assumes prompt is isolated (strip lines if needed)
USER_EXEC_PROMPT = re.compile(r'^\([^\)]+\) >$')      # e.g., (M4300-52G-PoE+) >
PRIV_EXEC_PROMPT = re.compile(r'^\([^\)]+\) #$')      # e.g., (M4300-52G-PoE+) #
GLOBAL_CONFIG_PROMPT = re.compile(r'^\([^\)]+\) \(Config\)#$')  # e.g., (M4300-52G-PoE+) (Config)#
VLAN_DATABASE_PROMPT = re.compile(r'^\([^\)]+\) \(Vlan\)#$')  # e.g., (M4300-52G-PoE+) (Vlan)#
INTERFACE_CONFIG_PROMPT = re.compile(r'^\([^\)]+\) \(Interface [^\)]+\)#$')  # e.g., (M4300-52G-PoE+) (Interface 1/0/1)# - captures interface ID
LINE_CONSOLE_PROMPT = re.compile(r'^\([^\)]+\) \(Config-line\)#$')  # e.g., (M4300-52G-PoE+) (Config-line)#
LINE_TELNET_PROMPT = re.compile(r'^\([^\)]+\) \(Config-telnet\)#$')  # e.g., (M4300-52G-PoE+) (Config-telnet)#
LINE_SSH_PROMPT = re.compile(r'^\([^\)]+\) \(Config-ssh\)#$')  # e.g., (M4300-52G-PoE+) (Config-ssh)#
AAA_IAS_USER_PROMPT = re.compile(r'^\([^\)]+\) \(Config-IAS-User\)#$')  # e.g., (M4300-52G-PoE+) (Config-IAS-User)#
DHCP_POOL_PROMPT = re.compile(r'^\([^\)]+\) \(Config-dhcp-pool\)#$')  # e.g., (M4300-52G-PoE+) (Config-dhcp-pool)#
DHCPV6_POOL_PROMPT = re.compile(r'^\([^\)]+\) \(Config-dhcp6s-pool\)#$')  # e.g., (M4300-52G-PoE+) (Config-dhcp6s-pool)# - note "dhcp6s"
CAPTIVE_PORTAL_PROMPT = re.compile(r'^\([^\)]+\) \(Config-CP\)#$')  # e.g., (M4300-52G-PoE+) (Config-CP)#
CAPTIVE_PORTAL_INSTANCE_PROMPT = re.compile(r'^\([^\)]+\) \(Config-CP \d+\)#$')  # e.g., (M4300-52G-PoE+) (Config-CP 1)# - captures ID
OSPF_CONFIG_PROMPT = re.compile(r'^\([^\)]+\) \(config-router\)#$')  # e.g., (M4300-52G-PoE+) (config-router)# - note lowercase "config"
OSPFV3_CONFIG_PROMPT = re.compile(r'^\([^\)]+\) \(Config-rtr\)#$')  # e.g., (M4300-52G-PoE+) (Config-rtr)# - abbrev "rtr"
RIP_CONFIG_PROMPT = re.compile(r'^\([^\)]+\) \(Config-router\)#$')  # e.g., (M4300-52G-PoE+) (Config-router)# - uppercase "Config" variant
VLAN_ROUTING_CONFIG_PROMPT = re.compile(r'^\([^\)]+\) \(Vlan\)#$')  # Same as VLAN database; no distinct prompt in examples

PROMPT_PATTERNS = {
    'user_exec': USER_EXEC_PROMPT,
    'priv_exec': PRIV_EXEC_PROMPT,
    'global_config': GLOBAL_CONFIG_PROMPT,
    'vlan_database': VLAN_DATABASE_PROMPT,
    'interface_config': INTERFACE_CONFIG_PROMPT,
    'line_console': LINE_CONSOLE_PROMPT,
    'line_telnet': LINE_TELNET_PROMPT,
    'line_ssh': LINE_SSH_PROMPT,
    'aaa_ias_user': AAA_IAS_USER_PROMPT,
    'dhcp_pool': DHCP_POOL_PROMPT,
    'dhcpv6_pool': DHCPV6_POOL_PROMPT,
    'captive_portal': CAPTIVE_PORTAL_PROMPT,
    'captive_portal_instance': CAPTIVE_PORTAL_INSTANCE_PROMPT,
    'ospf_config': OSPF_CONFIG_PROMPT,
    'ospfv3_config': OSPFV3_CONFIG_PROMPT,
    'rip_config': RIP_CONFIG_PROMPT,
    'vlan_routing_config': VLAN_ROUTING_CONFIG_PROMPT
}

def recognize_prompt(output):
    """
    Recognize the CLI prompt mode from output.
    
    Args:
        output (str): Raw output line containing the prompt.
    
    Returns:
        str: The mode key from PROMPT_PATTERNS, or 'unknown'.
    """
    prompt = output.strip().splitlines()[-1].strip() if output else ''
    
    for mode, pattern in PROMPT_PATTERNS.items():
        if pattern.match(prompt):
            return mode
    return 'unknown'

# Example test (replace with actual outputs)
sample = "(M4300-52G-PoE+) (Config)#"
print(recognize_prompt(sample))  # Should return 'global_config'
