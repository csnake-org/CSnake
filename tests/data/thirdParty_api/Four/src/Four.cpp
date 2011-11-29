#include "Four.h"

namespace math
{

Four::Four()
: Three()
{
	// does nothing.
}

int Four::getFour() const
{
   return getThree() + 1;
}

} // namespace math
