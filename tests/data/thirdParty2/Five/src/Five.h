#ifndef FIVE_H
#define FIVE_H

// Exports
// This is a static lib, so don't import or export anything.
#define FIVE_EXPORT

namespace math
{

/**
* Five
* Class that returns a mysterious number.
*/
class FIVE_EXPORT Five
{
public:
   Five();
   int getFive() const;
private:
   int m_Five;
}; // class Five

} // namespace math

#endif // FIVE_H
