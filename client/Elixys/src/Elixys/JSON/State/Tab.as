package Elixys.JSON.State
{
	import Elixys.JSON.JSONObject;
	
	import flash.utils.flash_proxy;
	
	public class Tab extends JSONObject
	{
		// Constructor
		public function Tab(data:String, existingcontent:Object = null)
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
			return "tab";
		}

		// Data wrappers
		public function get Text():String
		{
			return super.flash_proxy::getProperty("text");
		}
		public function get ID():String
		{
			return super.flash_proxy::getProperty("id");
		}
		
		// Tab comparison function.  Returns true if the tabs are equal, false otherwise.
		public static function CompareTabs(pTabA:Tab, pTabB:Tab):Boolean
		{
			if (pTabA.Text != pTabB.Text)
			{
				return false;
			}
			if (pTabA.ID != pTabB.ID)
			{
				return false;
			}
			return true;
		}
		
		// Tab array comparison function.  Returns true if the arrays are equal, false otherwise.
		public static function CompareTabArrays(pTabsA:Array, pTabsB:Array):Boolean
		{
			if (pTabsA.length != pTabsB.length)
			{
				return false;
			}
			else
			{
				var pTabA:Tab, pTabB:Tab;
				for (var i:int = 0; i < pTabsA.length; ++i)
				{
					pTabA = pTabsA[i] as Tab;
					pTabB = pTabsB[i] as Tab;
					if (!CompareTabs(pTabA, pTabB))
					{
						return false;
					}
				}
			}
			return true;
		}
	}
}
