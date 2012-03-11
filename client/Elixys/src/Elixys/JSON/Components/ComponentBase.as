package Elixys.JSON.Components
{
	import Elixys.JSON.JSONObject;
	
	import flash.utils.flash_proxy;
	
	public class ComponentBase extends JSONObject
	{
		// Constructor
		public function ComponentBase(data:String = null, existingcontent:Object = null)
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
			return "component";
		}

		// Data wrappers
		public function get ComponentType():String
		{
			return super.flash_proxy::getProperty("componenttype");
		}
		public function set ComponentType(value:String):void
		{
			super.flash_proxy::setProperty("componenttype", value);
		}

		public function get ID():uint
		{
			return super.flash_proxy::getProperty("id");
		}
		public function set ID(value:uint):void
		{
			super.flash_proxy::setProperty("id", value);
		}
		
		public function get Name():String
		{
			return super.flash_proxy::getProperty("name");
		}
		public function set Name(value:String):void
		{
			super.flash_proxy::setProperty("name", value);
		}

		public function get ValidationError():Boolean
		{
			return super.flash_proxy::getProperty("validationerror");
		}
		public function set ValidationError(value:Boolean):void
		{
			super.flash_proxy::setProperty("validationerror", value);
		}
		
		// Overridden by derived classes to format additional component details
		protected function FormatComponentDetails():String
		{
			return "";
		}

		// Convert to a JSON string
		public override function toString():String
		{
			// Give our derived class a chance to format additional details
			var sAdditionalDetails:String = FormatComponentDetails();
			
			// Create a JSON response string that will be recognized by the server
			var sJSON:String = "{";
			sJSON += JSONDataString("type", Type);
			sJSON += JSONDataString("componenttype", ComponentType);
			sJSON += JSONDataString("name", Name);
			sJSON += JSONDataObject("id", ID, sAdditionalDetails != "");
			if (sAdditionalDetails != "")
			{
				sJSON += sAdditionalDetails;
			}
			sJSON += "}";
			return sJSON;
		}
		
		// Component comparison function.  Returns true if the components are equal, false otherwise.
		public static function CompareComponents(pComponentA:ComponentBase, pComponentB:ComponentBase):Boolean
		{
			if (pComponentA.ComponentType != pComponentB.ComponentType)
			{
				return false;
			}
			if (pComponentA.ID != pComponentB.ID)
			{
				return false;
			}
			if (pComponentA.Name != pComponentB.Name)
			{
				return false;
			}
			if (pComponentA.ValidationError != pComponentB.ValidationError)
			{
				return false;
			}
			return true;
		}

		// Component array comparison function.  Returns true if the arrays are equal, false otherwise.
		public static function CompareComponentArrays(pComponentsA:Array, pComponentsB:Array):Boolean
		{
			if (pComponentsA.length != pComponentsB.length)
			{
				return false;
			}
			else
			{
				var pComponentA:ComponentBase, pComponentB:ComponentBase;
				for (var i:int = 0; i < pComponentsB.length; ++i)
				{
					pComponentA = pComponentsA[i] as ComponentBase;
					pComponentB = pComponentsB[i] as ComponentBase;
					if (!CompareComponents(pComponentA, pComponentB))
					{
						return false;
					}
				}
			}
			return true;
		}
	}
}
