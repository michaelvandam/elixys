package Elixys.JSON.State
{
	import Elixys.JSON.JSONObject;
	
	import flash.utils.flash_proxy;
	
	public class Column extends JSONObject
	{
		// Constructor
		public function Column(data:String, existingcontent:Object = null)
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
			return "column";
		}

		// Data wrappers
		public function get Data():String
		{
			return super.flash_proxy::getProperty("data");
		}
		public function get Display():String
		{
			return super.flash_proxy::getProperty("display");
		}
		public function get PercentWidth():int
		{
			return super.flash_proxy::getProperty("percentwidth");
		}
		public function get Sortable():Boolean
		{
			return super.flash_proxy::getProperty("sortable");
		}
		public function get SortMode():String
		{
			return super.flash_proxy::getProperty("sortmode");
		}
		
		// Column comparison function.  Returns true if the columns are equal, false otherwise.
		public static function CompareColumns(pColumnA:Column, pColumnB:Column):Boolean
		{
			if (pColumnA.Data != pColumnB.Data)
			{
				return false;
			}
			if (pColumnA.Display != pColumnB.Display)
			{
				return false;
			}
			if (pColumnA.PercentWidth != pColumnB.PercentWidth)
			{
				return false;
			}
			if (pColumnA.Sortable != pColumnB.Sortable)
			{
				return false;
			}
			if (pColumnA.SortMode != pColumnB.SortMode)
			{
				return false;
			}
			return true;
		}
		
		// Column array comparison function.  Returns true if the arrays are equal, false otherwise.
		public static function CompareColumnArrays(pColumnsA:Array, pColumnsB:Array):Boolean
		{
			if (pColumnsA.length != pColumnsB.length)
			{
				return false;
			}
			else
			{
				var pColumnA:Column, pColumnB:Column;
				for (var i:int = 0; i < pColumnsA.length; ++i)
				{
					pColumnA = pColumnsA[i] as Column;
					pColumnB = pColumnsB[i] as Column;
					if (!CompareColumns(pColumnA, pColumnB))
					{
						return false;
					}
				}
			}
			return true;
		}
	}
}
