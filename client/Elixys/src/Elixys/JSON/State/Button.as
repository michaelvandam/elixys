package Elixys.JSON.State
{
	import Elixys.JSON.JSONObject;
	
	import flash.utils.flash_proxy;
	
	public class Button extends JSONObject
	{
		// Constructor
		public function Button(data:String, existingcontent:Object = null)
		{
			// Call the base constructor
			super(data, existingcontent);
			
			// Validate the object type
			if ((Type != null) && (Type != TYPE))
			{
				throw new Error("Object type mismatch");
			}
		}

		// Static type
		public static function get TYPE():String
		{
			return "button";
		}

		// Data wrappers
		public function get ID():String
		{
			return super.flash_proxy::getProperty("id");
		}
		public function get Enabled():Boolean
		{
			return super.flash_proxy::getProperty("enabled");
		}

		// Button comparison function.  Returns true if the buttons are equal, false otherwise.
		public static function CompareButtons(pButtonA:Button, pButtonB:Button):Boolean
		{
			if (pButtonA.ID != pButtonB.ID)
			{
				return false;
			}
			if (pButtonA.Enabled != pButtonB.Enabled)
			{
				return false;
			}
			return true;
		}
		
		// Button array comparison function.  Returns true if the arrays are equal, false otherwise.
		public static function CompareButtonArrays(pButtonsA:Array, pButtonsB:Array):Boolean
		{
			if (pButtonsA.length != pButtonsB.length)
			{
				return false;
			}
			else
			{
				var pButtonA:Button, pButtonB:Button;
				for (var i:int = 0; i < pButtonsA.length; ++i)
				{
					pButtonA = pButtonsA[i] as Button;
					pButtonB = pButtonsB[i] as Button;
					if (!CompareButtons(pButtonA, pButtonB))
					{
						return false;
					}
				}
			}
			return true;
		}
	}
}
