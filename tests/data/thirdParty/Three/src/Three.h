#ifndef THREE_H
#define THREE_H

// Exports
// This is a static lib, so don't import or export anything.
#define THREE_EXPORT

namespace math
{

/**
* Three
* Class that returns a mysterious number.
*/
class THREE_EXPORT Three
{
public:
   Three();
   int getThree() const;
private:
   int m_three;
}; // class Three

} // namespace math

#endif // THREE_H
