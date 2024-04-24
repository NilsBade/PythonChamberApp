# just a random sample test that fails

def test_some_primes():
    assert 45 in {
        num
        for num in range(2, 50)
        if not any(num % div == 0 for div in range(2, num))
    }