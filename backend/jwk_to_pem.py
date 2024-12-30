from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import base64

# Replace with your values from JWK
n = "nWDHSQIViWxAMfOYY0EBHladcbQ8qsYtuCOZsIcGFQkONmlaowm-5-rj8XUP_VZPV34CBzQRIsZmW8bI95xJHnKrvn9HyBJ64Vjo4GTcD0AI86cbrj8inEIs3l_sQMKSZai2k2E7DQVUarJS6H_MSiMXsEj0Y1idnHaT3Oo0Muny8GY1X2kQ6Ck4agctElHU1_9DyCe4MoJXAxE5ZoSRAySGwtGk4yiyD2TVIKYeoVvV0tudn5WGqverxoUV6_PTu1DUk8xUSHywdYkdPjQgBW8Z36Z3jkkTmxm58Pyej4hKHcAcV7pEDHtJ3INA6ETJiC4G_1Dx9AjXh1shufoJhQ"
e = "AQAB"

def jwk_to_pem(n, e):
    n_int = int.from_bytes(base64.urlsafe_b64decode(n + '=='), 'big')
    e_int = int.from_bytes(base64.urlsafe_b64decode(e + '=='), 'big')
    public_numbers = rsa.RSAPublicNumbers(e_int, n_int)
    public_key = public_numbers.public_key()
    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

pem_key = jwk_to_pem(n, e)
print(pem_key.decode())
