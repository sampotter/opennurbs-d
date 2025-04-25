// Vibes...
struct atomic(T) {
  shared(T) value;
}

struct atomic_flag {
  byte[1] _;
}

struct shared_ptr(T) {
  byte[2*size_t.sizeof] _;
}

struct weak_ptr(T) {
  byte[2*size_t.sizeof] _;
}

// NOTE: sizeof(std::unique_ptr<T>) == sizeof(T*) for a default deleter
struct unique_ptr(T) {
  byte[size_t.sizeof] _;
}

struct vector(T) {
  byte[3*size_t.sizeof] _; // wild guess :-)
}
