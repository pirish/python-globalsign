from OpenSSL.crypto import load_certificate_request, FILETYPE_PEM

def get_base_domain(site):
    parts = site.split(".")
    return parts[-2] + "." + parts[-1]


def get_site(csr):
    req = load_certificate_request(FILETYPE_PEM, csr)
    subject = req.get_subject()
    components = dict(subject.get_components())
    return components['CN']

